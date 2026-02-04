"""Snowflake data profiling engine.

Executes profiling queries against Snowflake using a Snowpark Session
and returns structured results for each column including statistics,
distributions, and quality metrics.

Designed for Streamlit in Snowflake (SiS) — uses session.sql() instead
of snowflake.connector cursors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

try:
    from snowflake.snowpark import Session
except ImportError:
    Session = None  # Not available outside Snowflake


# ── Type classification ──────────────────────────────────────────────────────

NUMERIC_TYPES = {
    "NUMBER", "DECIMAL", "NUMERIC", "INT", "INTEGER", "BIGINT", "SMALLINT",
    "TINYINT", "BYTEINT", "FLOAT", "FLOAT4", "FLOAT8", "DOUBLE",
    "DOUBLE PRECISION", "REAL",
}

STRING_TYPES = {
    "VARCHAR", "CHAR", "CHARACTER", "STRING", "TEXT",
}

DATE_TYPES = {
    "DATE", "DATETIME", "TIMESTAMP", "TIMESTAMP_LTZ", "TIMESTAMP_NTZ",
    "TIMESTAMP_TZ", "TIME",
}

BOOLEAN_TYPES = {"BOOLEAN"}


def classify_type(raw_type: str) -> str:
    base = raw_type.upper().split("(")[0].strip()
    if base in NUMERIC_TYPES:
        return "numeric"
    if base in STRING_TYPES:
        return "string"
    if base in DATE_TYPES:
        return "date"
    if base in BOOLEAN_TYPES:
        return "boolean"
    return "other"


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ColumnProfile:
    name: str
    data_type: str
    type_category: str
    ordinal_position: int
    is_nullable: bool
    # Counts
    total_count: int = 0
    null_count: int = 0
    distinct_count: int = 0
    # Derived
    completeness_pct: float = 0.0
    uniqueness_pct: float = 0.0
    # Numeric stats
    min_value: Any = None
    max_value: Any = None
    mean_value: float | None = None
    median_value: float | None = None
    stddev_value: float | None = None
    sum_value: float | None = None
    p25: float | None = None
    p75: float | None = None
    p05: float | None = None
    p95: float | None = None
    # String stats
    min_length: int | None = None
    max_length: int | None = None
    avg_length: float | None = None
    empty_string_count: int = 0
    # Date stats
    min_date: str | None = None
    max_date: str | None = None
    date_range_days: int | None = None
    # Boolean stats
    true_count: int = 0
    false_count: int = 0
    # Top values
    top_values: list[dict] = field(default_factory=list)
    # Histogram data (for numeric columns)
    histogram: list[dict] = field(default_factory=list)

    @property
    def non_null_count(self) -> int:
        return self.total_count - self.null_count


@dataclass
class TableProfile:
    database: str
    schema: str
    table_name: str
    table_type: str  # TABLE or VIEW
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    profiled_at: str  # ISO timestamp
    # Aggregate quality
    overall_completeness: float = 0.0
    overall_uniqueness: float = 0.0
    quality_score: float = 0.0
    size_bytes: int | None = None
    # Warnings
    warnings: list[str] = field(default_factory=list)


# ── Profiler ─────────────────────────────────────────────────────────────────

class SnowflakeProfiler:
    """Profiles Snowflake tables and views using Snowpark Session SQL."""

    def __init__(self, session: Session):
        self.session = session

    def _q(self, sql: str) -> pd.DataFrame:
        """Execute SQL via Snowpark and return a pandas DataFrame."""
        return self.session.sql(sql).to_pandas()

    def list_databases(self) -> list[str]:
        df = self._q("SHOW DATABASES")
        return sorted(df["name"].tolist()) if "name" in df.columns else []

    def list_schemas(self, database: str) -> list[str]:
        df = self._q(f'SHOW SCHEMAS IN DATABASE "{database}"')
        return sorted(df["name"].tolist()) if "name" in df.columns else []

    def list_tables(self, database: str, schema: str) -> list[dict]:
        sql = f"""
            SELECT TABLE_NAME, TABLE_TYPE
            FROM "{database}".INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = '{schema}'
            AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
            ORDER BY TABLE_TYPE, TABLE_NAME
        """
        df = self._q(sql)
        if df.empty:
            return []
        return df.to_dict("records")

    def _get_columns(self, database: str, schema: str, table: str) -> pd.DataFrame:
        sql = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                ORDINAL_POSITION,
                IS_NULLABLE
            FROM "{database}".INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
        """
        return self._q(sql)

    def _get_row_count(self, fqn: str) -> int:
        df = self._q(f"SELECT COUNT(*) AS CNT FROM {fqn}")
        return int(df.iloc[0]["CNT"])

    def _get_table_size(self, database: str, schema: str, table: str) -> int | None:
        try:
            sql = f"""
                SELECT BYTES
                FROM "{database}".INFORMATION_SCHEMA.TABLE_STORAGE_METRICS
                WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
                LIMIT 1
            """
            df = self._q(sql)
            if not df.empty and "BYTES" in df.columns:
                return int(df.iloc[0]["BYTES"])
        except Exception:
            pass
        return None

    def profile_table(
        self,
        database: str,
        schema: str,
        table: str,
        table_type: str = "BASE TABLE",
        sample_size: int | None = None,
        progress_callback=None,
    ) -> TableProfile:
        fqn = f'"{database}"."{schema}"."{table}"'

        source = fqn
        if sample_size:
            source = f"(SELECT * FROM {fqn} LIMIT {sample_size})"

        col_df = self._get_columns(database, schema, table)
        row_count = self._get_row_count(source)
        size_bytes = self._get_table_size(database, schema, table)

        columns: list[ColumnProfile] = []
        total_cols = len(col_df)

        for idx, row in col_df.iterrows():
            col_name = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            ordinal = int(row["ORDINAL_POSITION"])
            nullable = row["IS_NULLABLE"] == "YES"
            type_cat = classify_type(data_type)

            if progress_callback:
                progress_callback(int(idx) + 1, total_cols, col_name)

            cp = ColumnProfile(
                name=col_name,
                data_type=data_type,
                type_category=type_cat,
                ordinal_position=ordinal,
                is_nullable=nullable,
                total_count=row_count,
            )

            self._profile_base_stats(cp, source)

            if type_cat == "numeric" and cp.non_null_count > 0:
                self._profile_numeric(cp, source)
            elif type_cat == "string" and cp.non_null_count > 0:
                self._profile_string(cp, source)
            elif type_cat == "date" and cp.non_null_count > 0:
                self._profile_date(cp, source)
            elif type_cat == "boolean" and cp.non_null_count > 0:
                self._profile_boolean(cp, source)

            if cp.non_null_count > 0:
                self._profile_top_values(cp, source)

            columns.append(cp)

        import datetime

        completeness_vals = [c.completeness_pct for c in columns]
        uniqueness_vals = [c.uniqueness_pct for c in columns if c.type_category != "boolean"]
        overall_completeness = sum(completeness_vals) / len(completeness_vals) if completeness_vals else 0
        overall_uniqueness = sum(uniqueness_vals) / len(uniqueness_vals) if uniqueness_vals else 0

        quality_score = (overall_completeness * 0.6) + (overall_uniqueness * 0.15)
        if row_count > 0:
            quality_score += 15
        type_cats = set(c.type_category for c in columns)
        quality_score += min(len(type_cats) * 2.5, 10)
        quality_score = min(quality_score, 100)

        warnings = self._generate_warnings(columns, row_count)

        return TableProfile(
            database=database,
            schema=schema,
            table_name=table,
            table_type=table_type,
            row_count=row_count,
            column_count=total_cols,
            columns=columns,
            profiled_at=datetime.datetime.now().isoformat(),
            overall_completeness=overall_completeness,
            overall_uniqueness=overall_uniqueness,
            quality_score=quality_score,
            size_bytes=size_bytes,
            warnings=warnings,
        )

    def _profile_base_stats(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                COUNT(*) AS TOTAL_COUNT,
                COUNT({col}) AS NON_NULL_COUNT,
                COUNT(*) - COUNT({col}) AS NULL_COUNT,
                COUNT(DISTINCT {col}) AS DISTINCT_COUNT
            FROM {source}
        """
        df = self._q(sql)
        r = df.iloc[0]
        cp.total_count = int(r["TOTAL_COUNT"])
        cp.null_count = int(r["NULL_COUNT"])
        cp.distinct_count = int(r["DISTINCT_COUNT"])
        cp.completeness_pct = (cp.non_null_count / cp.total_count * 100) if cp.total_count > 0 else 0
        cp.uniqueness_pct = (cp.distinct_count / cp.non_null_count * 100) if cp.non_null_count > 0 else 0

    def _profile_numeric(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                MIN({col}) AS MIN_VAL,
                MAX({col}) AS MAX_VAL,
                AVG({col}) AS MEAN_VAL,
                MEDIAN({col}) AS MEDIAN_VAL,
                STDDEV({col}) AS STDDEV_VAL,
                SUM({col}) AS SUM_VAL,
                PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY {col}) AS P05,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {col}) AS P25,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {col}) AS P75,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY {col}) AS P95
            FROM {source}
            WHERE {col} IS NOT NULL
        """
        df = self._q(sql)
        r = df.iloc[0]
        cp.min_value = _safe_num(r.get("MIN_VAL"))
        cp.max_value = _safe_num(r.get("MAX_VAL"))
        cp.mean_value = _safe_float(r.get("MEAN_VAL"))
        cp.median_value = _safe_float(r.get("MEDIAN_VAL"))
        cp.stddev_value = _safe_float(r.get("STDDEV_VAL"))
        cp.sum_value = _safe_float(r.get("SUM_VAL"))
        cp.p05 = _safe_float(r.get("P05"))
        cp.p25 = _safe_float(r.get("P25"))
        cp.p75 = _safe_float(r.get("P75"))
        cp.p95 = _safe_float(r.get("P95"))

        self._profile_numeric_histogram(cp, source)

    def _profile_numeric_histogram(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        num_bins = 20
        try:
            sql = f"""
                WITH bounds AS (
                    SELECT
                        MIN({col})::FLOAT AS MIN_V,
                        MAX({col})::FLOAT AS MAX_V
                    FROM {source}
                    WHERE {col} IS NOT NULL
                ),
                binned AS (
                    SELECT
                        LEAST(
                            FLOOR(({col}::FLOAT - b.MIN_V) / NULLIF((b.MAX_V - b.MIN_V) / {num_bins}, 0)),
                            {num_bins - 1}
                        ) AS BIN_IDX,
                        b.MIN_V,
                        b.MAX_V
                    FROM {source}, bounds b
                    WHERE {col} IS NOT NULL
                )
                SELECT
                    BIN_IDX,
                    COUNT(*) AS CNT,
                    MIN(MIN_V) AS MIN_V,
                    MIN(MAX_V) AS MAX_V
                FROM binned
                GROUP BY BIN_IDX
                ORDER BY BIN_IDX
            """
            df = self._q(sql)
            if df.empty:
                return
            min_v = float(df.iloc[0]["MIN_V"])
            max_v = float(df.iloc[0]["MAX_V"])
            bin_width = (max_v - min_v) / num_bins if max_v != min_v else 1
            hist = []
            for _, r in df.iterrows():
                b = int(r["BIN_IDX"]) if r["BIN_IDX"] is not None else 0
                hist.append({
                    "bin": b,
                    "low": round(min_v + b * bin_width, 4),
                    "high": round(min_v + (b + 1) * bin_width, 4),
                    "count": int(r["CNT"]),
                })
            cp.histogram = hist
        except Exception:
            pass

    def _profile_string(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                MIN(LENGTH({col})) AS MIN_LEN,
                MAX(LENGTH({col})) AS MAX_LEN,
                AVG(LENGTH({col})) AS AVG_LEN,
                SUM(CASE WHEN {col} = '' THEN 1 ELSE 0 END) AS EMPTY_COUNT,
                MIN({col}) AS MIN_VAL,
                MAX({col}) AS MAX_VAL
            FROM {source}
            WHERE {col} IS NOT NULL
        """
        df = self._q(sql)
        r = df.iloc[0]
        cp.min_length = _safe_int(r.get("MIN_LEN"))
        cp.max_length = _safe_int(r.get("MAX_LEN"))
        cp.avg_length = _safe_float(r.get("AVG_LEN"))
        cp.empty_string_count = _safe_int(r.get("EMPTY_COUNT")) or 0
        cp.min_value = r.get("MIN_VAL")
        cp.max_value = r.get("MAX_VAL")

    def _profile_date(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                MIN({col})::VARCHAR AS MIN_DT,
                MAX({col})::VARCHAR AS MAX_DT,
                DATEDIFF('day', MIN({col}), MAX({col})) AS RANGE_DAYS
            FROM {source}
            WHERE {col} IS NOT NULL
        """
        df = self._q(sql)
        r = df.iloc[0]
        cp.min_date = str(r.get("MIN_DT", ""))
        cp.max_date = str(r.get("MAX_DT", ""))
        cp.date_range_days = _safe_int(r.get("RANGE_DAYS"))
        cp.min_value = cp.min_date
        cp.max_value = cp.max_date

    def _profile_boolean(self, cp: ColumnProfile, source: str):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                SUM(CASE WHEN {col} = TRUE THEN 1 ELSE 0 END) AS TRUE_COUNT,
                SUM(CASE WHEN {col} = FALSE THEN 1 ELSE 0 END) AS FALSE_COUNT
            FROM {source}
            WHERE {col} IS NOT NULL
        """
        df = self._q(sql)
        r = df.iloc[0]
        cp.true_count = _safe_int(r.get("TRUE_COUNT")) or 0
        cp.false_count = _safe_int(r.get("FALSE_COUNT")) or 0

    def _profile_top_values(self, cp: ColumnProfile, source: str, limit: int = 10):
        col = f'"{cp.name}"'
        sql = f"""
            SELECT
                {col}::VARCHAR AS VAL,
                COUNT(*) AS CNT
            FROM {source}
            WHERE {col} IS NOT NULL
            GROUP BY {col}
            ORDER BY CNT DESC
            LIMIT {limit}
        """
        try:
            df = self._q(sql)
            top = []
            for _, r in df.iterrows():
                top.append({
                    "value": str(r["VAL"]) if r["VAL"] is not None else "NULL",
                    "count": int(r["CNT"]),
                    "pct": round(int(r["CNT"]) / cp.non_null_count * 100, 2) if cp.non_null_count else 0,
                })
            cp.top_values = top
        except Exception:
            pass

    def _generate_warnings(self, columns: list[ColumnProfile], row_count: int) -> list[str]:
        warnings = []
        if row_count == 0:
            warnings.append("Table is empty - no data to profile.")
            return warnings

        for c in columns:
            if c.completeness_pct < 50:
                warnings.append(f'Column "{c.name}" is more than 50% null ({c.null_count:,} nulls).')
            if c.uniqueness_pct == 100 and c.non_null_count > 1:
                warnings.append(f'Column "{c.name}" has all unique values - potential ID or key column.')
            if c.type_category == "string" and c.empty_string_count and c.empty_string_count > row_count * 0.1:
                warnings.append(f'Column "{c.name}" has {c.empty_string_count:,} empty strings.')
            if c.distinct_count == 1 and c.non_null_count > 0:
                warnings.append(f'Column "{c.name}" contains only a single distinct value.')
            if c.type_category == "numeric" and c.stddev_value == 0 and c.non_null_count > 1:
                warnings.append(f'Column "{c.name}" has zero variance (all values identical).')

        return warnings


# ── Helpers ──────────────────────────────────────────────────────────────────

def _safe_float(val) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _safe_num(val):
    if val is None:
        return None
    try:
        f = float(val)
        if f == int(f):
            return int(f)
        return round(f, 4)
    except (ValueError, TypeError):
        return val
