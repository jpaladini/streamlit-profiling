"""Generates realistic mock profiling data for preview mode.

Used when the app is running outside Snowflake (no active session)
so the full UI can be previewed with representative data.
"""

from __future__ import annotations

import datetime
from profiler import ColumnProfile, TableProfile


def generate_mock_profile() -> TableProfile:
    """Return a realistic TableProfile for a fictional e-commerce orders table."""

    columns = [
        _mock_id_column(),
        _mock_customer_id_column(),
        _mock_order_date_column(),
        _mock_status_column(),
        _mock_total_amount_column(),
        _mock_quantity_column(),
        _mock_email_column(),
        _mock_shipping_country_column(),
        _mock_discount_pct_column(),
        _mock_is_returned_column(),
        _mock_notes_column(),
    ]

    completeness_vals = [c.completeness_pct for c in columns]
    uniqueness_vals = [c.uniqueness_pct for c in columns if c.type_category != "boolean"]
    overall_completeness = sum(completeness_vals) / len(completeness_vals)
    overall_uniqueness = sum(uniqueness_vals) / len(uniqueness_vals)
    quality_score = 87.3

    return TableProfile(
        database="ANALYTICS",
        schema="PUBLIC",
        table_name="ORDERS",
        table_type="BASE TABLE",
        row_count=248_519,
        column_count=len(columns),
        columns=columns,
        profiled_at=datetime.datetime.now().isoformat(),
        overall_completeness=overall_completeness,
        overall_uniqueness=overall_uniqueness,
        quality_score=quality_score,
        size_bytes=184_320_000,
        warnings=[
            'Column "NOTES" is more than 50% null (167,250 nulls).',
            'Column "ORDER_ID" has all unique values - potential ID or key column.',
            'Column "CUSTOMER_ID" has all unique values - potential ID or key column.',
            'Column "DISCOUNT_PCT" contains only 8 distinct values - consider using a category type.',
        ],
    )


def _mock_id_column() -> ColumnProfile:
    return ColumnProfile(
        name="ORDER_ID",
        data_type="NUMBER",
        type_category="numeric",
        ordinal_position=1,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=248_519,
        completeness_pct=100.0,
        uniqueness_pct=100.0,
        min_value=1,
        max_value=248_519,
        mean_value=124_260.0,
        median_value=124_260.0,
        stddev_value=71_741.8,
        sum_value=30_893_947_140,
        p05=12_426.0,
        p25=62_130.0,
        p75=186_390.0,
        p95=236_093.0,
        histogram=[
            {"bin": i, "low": 1 + i * 12426, "high": 1 + (i + 1) * 12426, "count": c}
            for i, c in enumerate([
                12480, 12510, 12390, 12450, 12520, 12400, 12460, 12530, 12410, 12470,
                12540, 12420, 12480, 12390, 12510, 12450, 12400, 12520, 12460, 12199,
            ])
        ],
        top_values=[
            {"value": str(248519 - i), "count": 1, "pct": 0.0} for i in range(10)
        ],
    )


def _mock_customer_id_column() -> ColumnProfile:
    return ColumnProfile(
        name="CUSTOMER_ID",
        data_type="VARCHAR",
        type_category="string",
        ordinal_position=2,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=45_230,
        completeness_pct=100.0,
        uniqueness_pct=18.2,
        min_length=8,
        max_length=12,
        avg_length=10.3,
        empty_string_count=0,
        min_value="CUST-00001",
        max_value="CUST-45230",
        top_values=[
            {"value": "CUST-11204", "count": 42, "pct": 0.02},
            {"value": "CUST-30891", "count": 38, "pct": 0.02},
            {"value": "CUST-07553", "count": 35, "pct": 0.01},
            {"value": "CUST-22140", "count": 33, "pct": 0.01},
            {"value": "CUST-41002", "count": 31, "pct": 0.01},
            {"value": "CUST-15678", "count": 29, "pct": 0.01},
            {"value": "CUST-38421", "count": 27, "pct": 0.01},
            {"value": "CUST-09100", "count": 25, "pct": 0.01},
        ],
    )


def _mock_order_date_column() -> ColumnProfile:
    return ColumnProfile(
        name="ORDER_DATE",
        data_type="TIMESTAMP_NTZ",
        type_category="date",
        ordinal_position=3,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=1_096,
        completeness_pct=100.0,
        uniqueness_pct=0.44,
        min_date="2021-01-01 00:00:00",
        max_date="2024-12-31 23:59:59",
        date_range_days=1_461,
        min_value="2021-01-01",
        max_value="2024-12-31",
        top_values=[
            {"value": "2024-11-29", "count": 1_842, "pct": 0.74},
            {"value": "2024-12-23", "count": 1_605, "pct": 0.65},
            {"value": "2024-07-04", "count": 1_410, "pct": 0.57},
            {"value": "2024-11-25", "count": 1_380, "pct": 0.56},
            {"value": "2023-11-24", "count": 1_290, "pct": 0.52},
            {"value": "2023-12-22", "count": 1_201, "pct": 0.48},
        ],
    )


def _mock_status_column() -> ColumnProfile:
    return ColumnProfile(
        name="STATUS",
        data_type="VARCHAR",
        type_category="string",
        ordinal_position=4,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=5,
        completeness_pct=100.0,
        uniqueness_pct=0.002,
        min_length=4,
        max_length=10,
        avg_length=7.2,
        empty_string_count=0,
        min_value="CANCELLED",
        max_value="SHIPPED",
        top_values=[
            {"value": "DELIVERED", "count": 149_111, "pct": 60.0},
            {"value": "SHIPPED", "count": 49_704, "pct": 20.0},
            {"value": "PROCESSING", "count": 24_852, "pct": 10.0},
            {"value": "PENDING", "count": 17_396, "pct": 7.0},
            {"value": "CANCELLED", "count": 7_456, "pct": 3.0},
        ],
    )


def _mock_total_amount_column() -> ColumnProfile:
    return ColumnProfile(
        name="TOTAL_AMOUNT",
        data_type="NUMBER",
        type_category="numeric",
        ordinal_position=5,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=18_432,
        completeness_pct=100.0,
        uniqueness_pct=7.42,
        min_value=1.99,
        max_value=4_999.99,
        mean_value=187.43,
        median_value=129.95,
        stddev_value=215.67,
        sum_value=46_580_125.50,
        p05=9.99,
        p25=49.95,
        p75=249.99,
        p95=699.99,
        histogram=[
            {"bin": i, "low": round(1.99 + i * 250, 2), "high": round(1.99 + (i + 1) * 250, 2), "count": c}
            for i, c in enumerate([
                74_556, 62_130, 42_048, 27_337, 17_396, 9_941, 6_213, 3_726, 2_236, 1_118,
                745, 497, 298, 199, 125, 75, 45, 20, 10, 4,
            ])
        ],
        top_values=[
            {"value": "29.99", "count": 3_210, "pct": 1.29},
            {"value": "49.99", "count": 2_890, "pct": 1.16},
            {"value": "99.99", "count": 2_541, "pct": 1.02},
            {"value": "19.99", "count": 2_102, "pct": 0.85},
            {"value": "149.99", "count": 1_870, "pct": 0.75},
            {"value": "9.99", "count": 1_654, "pct": 0.67},
            {"value": "199.99", "count": 1_420, "pct": 0.57},
            {"value": "79.99", "count": 1_310, "pct": 0.53},
        ],
    )


def _mock_quantity_column() -> ColumnProfile:
    return ColumnProfile(
        name="QUANTITY",
        data_type="NUMBER",
        type_category="numeric",
        ordinal_position=6,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=25,
        completeness_pct=100.0,
        uniqueness_pct=0.01,
        min_value=1,
        max_value=25,
        mean_value=3.2,
        median_value=2.0,
        stddev_value=2.8,
        sum_value=795_261,
        p05=1.0,
        p25=1.0,
        p75=4.0,
        p95=10.0,
        histogram=[
            {"bin": i, "low": 1 + i * 1.2, "high": 1 + (i + 1) * 1.2, "count": c}
            for i, c in enumerate([
                89_467, 54_674, 34_793, 22_367, 14_911, 9_941, 6_956, 4_970, 3_478, 2_485,
                1_739, 1_118, 745, 497, 298, 199, 125, 75, 50, 31,
            ])
        ],
        top_values=[
            {"value": "1", "count": 89_467, "pct": 36.0},
            {"value": "2", "count": 54_674, "pct": 22.0},
            {"value": "3", "count": 34_793, "pct": 14.0},
            {"value": "4", "count": 22_367, "pct": 9.0},
            {"value": "5", "count": 14_911, "pct": 6.0},
            {"value": "6", "count": 9_941, "pct": 4.0},
        ],
    )


def _mock_email_column() -> ColumnProfile:
    return ColumnProfile(
        name="EMAIL",
        data_type="VARCHAR",
        type_category="string",
        ordinal_position=7,
        is_nullable=True,
        total_count=248_519,
        null_count=12_426,
        distinct_count=44_890,
        completeness_pct=95.0,
        uniqueness_pct=19.0,
        min_length=11,
        max_length=48,
        avg_length=24.6,
        empty_string_count=0,
        min_value="a.adams@example.com",
        max_value="z.zwick@testmail.org",
        top_values=[
            {"value": "info@company.com", "count": 156, "pct": 0.07},
            {"value": "sales@bigcorp.com", "count": 89, "pct": 0.04},
            {"value": "orders@retail.io", "count": 72, "pct": 0.03},
            {"value": "support@store.com", "count": 61, "pct": 0.03},
            {"value": "admin@shop.net", "count": 48, "pct": 0.02},
        ],
    )


def _mock_shipping_country_column() -> ColumnProfile:
    return ColumnProfile(
        name="SHIPPING_COUNTRY",
        data_type="VARCHAR",
        type_category="string",
        ordinal_position=8,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=38,
        completeness_pct=100.0,
        uniqueness_pct=0.015,
        min_length=2,
        max_length=24,
        avg_length=8.4,
        empty_string_count=0,
        min_value="Argentina",
        max_value="United States",
        top_values=[
            {"value": "United States", "count": 134_200, "pct": 54.0},
            {"value": "Canada", "count": 27_337, "pct": 11.0},
            {"value": "United Kingdom", "count": 22_367, "pct": 9.0},
            {"value": "Germany", "count": 14_911, "pct": 6.0},
            {"value": "France", "count": 12_426, "pct": 5.0},
            {"value": "Australia", "count": 9_941, "pct": 4.0},
            {"value": "Japan", "count": 7_456, "pct": 3.0},
            {"value": "Brazil", "count": 4_970, "pct": 2.0},
        ],
    )


def _mock_discount_pct_column() -> ColumnProfile:
    return ColumnProfile(
        name="DISCOUNT_PCT",
        data_type="NUMBER",
        type_category="numeric",
        ordinal_position=9,
        is_nullable=True,
        total_count=248_519,
        null_count=49_704,
        distinct_count=8,
        completeness_pct=80.0,
        uniqueness_pct=0.004,
        min_value=0,
        max_value=50,
        mean_value=11.3,
        median_value=10.0,
        stddev_value=10.5,
        sum_value=2_244_497,
        p05=0.0,
        p25=5.0,
        p75=15.0,
        p95=30.0,
        histogram=[
            {"bin": 0, "low": 0, "high": 5, "count": 69_585},
            {"bin": 1, "low": 5, "high": 10, "count": 54_674},
            {"bin": 2, "low": 10, "high": 15, "count": 37_278},
            {"bin": 3, "low": 15, "high": 20, "count": 19_882},
            {"bin": 4, "low": 20, "high": 25, "count": 9_941},
            {"bin": 5, "low": 25, "high": 30, "count": 4_970},
            {"bin": 6, "low": 30, "high": 40, "count": 1_739},
            {"bin": 7, "low": 40, "high": 50, "count": 746},
        ],
        top_values=[
            {"value": "0", "count": 69_585, "pct": 35.0},
            {"value": "5", "count": 39_763, "pct": 20.0},
            {"value": "10", "count": 37_278, "pct": 18.75},
            {"value": "15", "count": 19_882, "pct": 10.0},
            {"value": "20", "count": 14_911, "pct": 7.5},
            {"value": "25", "count": 9_941, "pct": 5.0},
            {"value": "30", "count": 4_970, "pct": 2.5},
            {"value": "50", "count": 2_485, "pct": 1.25},
        ],
    )


def _mock_is_returned_column() -> ColumnProfile:
    return ColumnProfile(
        name="IS_RETURNED",
        data_type="BOOLEAN",
        type_category="boolean",
        ordinal_position=10,
        is_nullable=False,
        total_count=248_519,
        null_count=0,
        distinct_count=2,
        completeness_pct=100.0,
        uniqueness_pct=0.0008,
        true_count=19_882,
        false_count=228_637,
        top_values=[
            {"value": "FALSE", "count": 228_637, "pct": 92.0},
            {"value": "TRUE", "count": 19_882, "pct": 8.0},
        ],
    )


def _mock_notes_column() -> ColumnProfile:
    return ColumnProfile(
        name="NOTES",
        data_type="VARCHAR",
        type_category="string",
        ordinal_position=11,
        is_nullable=True,
        total_count=248_519,
        null_count=167_250,
        distinct_count=78_210,
        completeness_pct=32.7,
        uniqueness_pct=96.2,
        min_length=3,
        max_length=500,
        avg_length=42.8,
        empty_string_count=320,
        min_value="...",
        max_value="zzz note",
        top_values=[
            {"value": "Gift wrapping requested", "count": 412, "pct": 0.51},
            {"value": "Rush delivery", "count": 389, "pct": 0.48},
            {"value": "Leave at door", "count": 341, "pct": 0.42},
            {"value": "Fragile", "count": 298, "pct": 0.37},
            {"value": "No signature required", "count": 210, "pct": 0.26},
        ],
    )
