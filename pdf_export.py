"""PDF report generation for Snowflake data profiling results.

Creates a professional, multi-page PDF report with charts, tables,
and quality metrics using fpdf2.
"""

from __future__ import annotations

import io
import math
from datetime import datetime

from fpdf import FPDF

from profiler import ColumnProfile, TableProfile


# ── Color palette ────────────────────────────────────────────────────────────

class C:
    """Color constants (R, G, B tuples)."""
    BG_DARK = (15, 23, 42)
    BG_CARD = (30, 41, 59)
    BG_STAT = (20, 30, 48)
    TEXT_PRIMARY = (226, 232, 240)
    TEXT_SECONDARY = (148, 163, 184)
    TEXT_MUTED = (100, 116, 139)
    INDIGO = (79, 70, 229)
    INDIGO_LIGHT = (129, 140, 248)
    PURPLE = (124, 58, 237)
    CYAN = (6, 182, 212)
    GREEN = (16, 185, 129)
    GREEN_LIGHT = (52, 211, 153)
    YELLOW = (245, 158, 11)
    RED = (239, 68, 68)
    PINK = (236, 72, 153)
    BLUE = (59, 130, 246)
    WHITE = (255, 255, 255)
    ACCENT_BAR = (79, 70, 229)
    BORDER = (51, 65, 85)


TYPE_COLORS = {
    "numeric": C.BLUE,
    "string": C.GREEN,
    "date": C.YELLOW,
    "boolean": C.PURPLE,
    "other": C.TEXT_MUTED,
}


# ── PDF Builder ──────────────────────────────────────────────────────────────

class ProfilePDF(FPDF):
    """Custom PDF class with dark-themed data profiling layout."""

    def __init__(self, profile: TableProfile):
        super().__init__("P", "mm", "A4")
        self.profile = profile
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(15, 15, 15)

    def header(self):
        if self.page_no() == 1:
            return  # Custom cover page
        self.set_fill_color(*C.BG_DARK)
        self.rect(0, 0, 210, 297, "F")
        # Top bar
        self.set_fill_color(*C.INDIGO)
        self.rect(0, 0, 210, 3, "F")
        # Header text
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*C.TEXT_SECONDARY)
        self.set_xy(15, 6)
        p = self.profile
        self.cell(0, 5, f"{p.database}.{p.schema}.{p.table_name}", align="L")
        self.set_xy(15, 6)
        self.cell(0, 5, f"Page {self.page_no()}", align="R")
        self.set_y(16)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*C.TEXT_MUTED)
        self.cell(0, 5, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  Snowflake Data Profiler", align="C")


def generate_pdf(profile: TableProfile) -> bytes:
    pdf = ProfilePDF(profile)
    pdf.add_page()

    _draw_cover(pdf, profile)
    pdf.add_page()
    _draw_overview(pdf, profile)
    _draw_quality_section(pdf, profile)
    _draw_warnings(pdf, profile)

    for i, col in enumerate(profile.columns):
        pdf.add_page()
        _draw_column_page(pdf, col, i + 1, len(profile.columns), profile.row_count)

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


# ── Cover page ───────────────────────────────────────────────────────────────

def _draw_cover(pdf: ProfilePDF, p: TableProfile):
    # Background
    pdf.set_fill_color(*C.BG_DARK)
    pdf.rect(0, 0, 210, 297, "F")

    # Gradient header block
    _draw_gradient_rect(pdf, 0, 0, 210, 130)

    # Title
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*C.WHITE)
    pdf.set_xy(20, 30)
    pdf.cell(170, 14, "Data Profile Report", align="L")

    # Subtitle
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(255, 255, 255)  # white with alpha simulated
    pdf.set_xy(20, 48)
    pdf.cell(170, 8, "Snowflake Table Analysis", align="L")

    # Table info
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(20, 68)
    pdf.cell(170, 10, f"{p.database}.{p.schema}", align="L")
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(20, 80)
    pdf.cell(170, 12, p.table_name, align="L")

    # Type badge
    pdf.set_font("Helvetica", "B", 9)
    badge_text = "VIEW" if p.table_type == "VIEW" else "TABLE"
    tw = pdf.get_string_width(badge_text) + 10
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(*C.INDIGO)
    pdf.set_xy(20, 96)
    pdf.cell(tw, 7, badge_text, fill=True, align="C")

    # Summary cards below the gradient
    y = 145
    cards = [
        ("Rows", f"{p.row_count:,}"),
        ("Columns", str(p.column_count)),
        ("Completeness", f"{p.overall_completeness:.1f}%"),
        ("Quality Score", f"{p.quality_score:.0f}/100"),
    ]

    card_w = 42
    gap = 4
    start_x = 15

    for i, (label, value) in enumerate(cards):
        x = start_x + i * (card_w + gap)
        _draw_stat_card(pdf, x, y, card_w, 30, label, value)

    # Profiled at
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*C.TEXT_MUTED)
    pdf.set_xy(15, 190)
    pdf.cell(180, 6, f"Profiled at: {p.profiled_at[:19].replace('T', ' ')}", align="L")

    if p.size_bytes is not None:
        pdf.set_xy(15, 198)
        pdf.cell(180, 6, f"Table size: {_fmt_bytes(p.size_bytes)}", align="L")


# ── Overview page ────────────────────────────────────────────────────────────

def _draw_overview(pdf: ProfilePDF, p: TableProfile):
    _draw_section_header(pdf, "Table Overview")

    y = pdf.get_y() + 2
    # Column summary table
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*C.TEXT_SECONDARY)
    headers = ["#", "Column", "Type", "Non-Null", "Distinct", "Complete %", "Unique %"]
    widths = [8, 44, 22, 22, 22, 28, 28]

    x = 15
    for i, h in enumerate(headers):
        pdf.set_xy(x, y)
        pdf.cell(widths[i], 6, h, align="L")
        x += widths[i]

    y += 8
    pdf.set_draw_color(*C.BORDER)
    pdf.line(15, y - 1, 195, y - 1)

    pdf.set_font("Helvetica", "", 8)
    for col in p.columns:
        if y > 265:
            pdf.add_page()
            y = pdf.get_y()

        pdf.set_text_color(*C.TEXT_PRIMARY)
        x = 15
        vals = [
            str(col.ordinal_position),
            col.name[:24],
            col.data_type[:12],
            f"{col.non_null_count:,}",
            f"{col.distinct_count:,}",
            f"{col.completeness_pct:.1f}%",
            f"{col.uniqueness_pct:.1f}%",
        ]
        for i, v in enumerate(vals):
            pdf.set_xy(x, y)
            if i == 2:
                tc = TYPE_COLORS.get(col.type_category, C.TEXT_MUTED)
                pdf.set_text_color(*tc)
            else:
                pdf.set_text_color(*C.TEXT_PRIMARY)
            pdf.cell(widths[i], 5.5, v, align="L")
            x += widths[i]
        y += 6.5

        # Light separator
        pdf.set_draw_color(40, 50, 70)
        pdf.line(15, y - 0.5, 195, y - 0.5)


# ── Quality ──────────────────────────────────────────────────────────────────

def _draw_quality_section(pdf: ProfilePDF, p: TableProfile):
    if pdf.get_y() > 200:
        pdf.add_page()

    _draw_section_header(pdf, "Data Quality")

    y = pdf.get_y() + 2
    score = p.quality_score
    color = C.GREEN if score >= 90 else C.BLUE if score >= 70 else C.YELLOW if score >= 50 else C.RED

    # Score display
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(*color)
    pdf.set_xy(15, y)
    pdf.cell(40, 20, f"{score:.0f}", align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*C.TEXT_SECONDARY)
    pdf.set_xy(55, y + 4)
    pdf.cell(40, 6, "/ 100", align="L")

    label = "Excellent" if score >= 90 else "Good" if score >= 70 else "Fair" if score >= 50 else "Needs Attention"
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*color)
    pdf.set_xy(55, y + 11)
    pdf.cell(40, 6, label, align="L")

    # Quality bars
    bars_x = 100
    bar_w = 85
    bar_h = 5

    items = [
        ("Completeness", p.overall_completeness),
        ("Uniqueness", p.overall_uniqueness),
    ]

    for i, (lbl, val) in enumerate(items):
        by = y + 2 + i * 14
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*C.TEXT_SECONDARY)
        pdf.set_xy(bars_x, by)
        pdf.cell(bar_w, 5, f"{lbl}: {val:.1f}%", align="L")

        # Bar background
        pdf.set_fill_color(*C.BG_STAT)
        pdf.rect(bars_x, by + 6, bar_w, bar_h, "F")

        # Bar fill
        fill_w = max(bar_w * val / 100, 0.5)
        fc = C.GREEN if val >= 90 else C.BLUE if val >= 70 else C.YELLOW if val >= 50 else C.RED
        pdf.set_fill_color(*fc)
        pdf.rect(bars_x, by + 6, fill_w, bar_h, "F")

    pdf.set_y(y + 35)


# ── Warnings ─────────────────────────────────────────────────────────────────

def _draw_warnings(pdf: ProfilePDF, p: TableProfile):
    if not p.warnings:
        return

    if pdf.get_y() > 230:
        pdf.add_page()

    _draw_section_header(pdf, f"Warnings ({len(p.warnings)})")

    y = pdf.get_y() + 2
    pdf.set_font("Helvetica", "", 8)

    for w in p.warnings[:15]:
        if y > 275:
            pdf.add_page()
            y = pdf.get_y()

        # Warning icon
        pdf.set_fill_color(*C.YELLOW)
        pdf.rect(15, y + 1, 3, 3, "F")

        pdf.set_text_color(*C.TEXT_PRIMARY)
        pdf.set_xy(21, y)
        pdf.cell(170, 5, w[:100], align="L")
        y += 7

    pdf.set_y(y + 3)


# ── Column detail page ──────────────────────────────────────────────────────

def _draw_column_page(pdf: ProfilePDF, col: ColumnProfile, idx: int, total: int, total_rows: int):
    # Column header
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*C.TEXT_PRIMARY)
    y = pdf.get_y()
    pdf.set_xy(15, y)
    pdf.cell(130, 10, col.name, align="L")

    # Type badge
    tc = TYPE_COLORS.get(col.type_category, C.TEXT_MUTED)
    pdf.set_font("Helvetica", "B", 8)
    badge = col.data_type
    bw = pdf.get_string_width(badge) + 8
    pdf.set_fill_color(*tc)
    pdf.set_text_color(*C.WHITE)
    pdf.set_xy(195 - bw, y + 2)
    pdf.cell(bw, 6, badge, fill=True, align="C")

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*C.TEXT_MUTED)
    pdf.set_xy(15, y + 11)
    pdf.cell(80, 5, f"Column {idx} of {total}  |  Position {col.ordinal_position}", align="L")

    y = y + 20

    # Stat cards row
    cards = [
        ("Total", f"{col.total_count:,}"),
        ("Non-Null", f"{col.non_null_count:,}"),
        ("Nulls", f"{col.null_count:,}"),
        ("Distinct", f"{col.distinct_count:,}"),
    ]
    card_w = 42
    for i, (lbl, val) in enumerate(cards):
        _draw_stat_card(pdf, 15 + i * (card_w + 3), y, card_w, 22, lbl, val)
    y += 28

    # Progress bars
    _draw_pdf_progress_bar(pdf, 15, y, 85, "Completeness", col.completeness_pct)
    _draw_pdf_progress_bar(pdf, 105, y, 85, "Uniqueness", col.uniqueness_pct)
    y += 18

    # Type-specific stats
    if col.type_category == "numeric":
        y = _draw_numeric_stats(pdf, col, y)
    elif col.type_category == "string":
        y = _draw_string_stats(pdf, col, y)
    elif col.type_category == "date":
        y = _draw_date_stats(pdf, col, y)
    elif col.type_category == "boolean":
        y = _draw_boolean_stats(pdf, col, y)

    # Top values
    if col.top_values:
        y = _draw_top_values(pdf, col, y, total_rows)


def _draw_numeric_stats(pdf: ProfilePDF, col: ColumnProfile, y: float) -> float:
    _draw_mini_section(pdf, "Statistics", y)
    y += 8

    stats = [
        ("Min", _fmt_num(col.min_value)),
        ("Max", _fmt_num(col.max_value)),
        ("Mean", _fmt_num(col.mean_value)),
        ("Median", _fmt_num(col.median_value)),
        ("Std Dev", _fmt_num(col.stddev_value)),
        ("Sum", _fmt_num(col.sum_value)),
        ("P5", _fmt_num(col.p05)),
        ("P25", _fmt_num(col.p25)),
        ("P75", _fmt_num(col.p75)),
        ("P95", _fmt_num(col.p95)),
    ]

    col_w = 36
    row_h = 14
    per_row = 5
    for i, (lbl, val) in enumerate(stats):
        r = i // per_row
        c = i % per_row
        _draw_stat_card(pdf, 15 + c * (col_w + 2), y + r * (row_h + 4), col_w, row_h, lbl, val)

    y += (math.ceil(len(stats) / per_row)) * (row_h + 4) + 4

    # Histogram
    if col.histogram:
        y = _draw_histogram(pdf, col, y)

    return y


def _draw_string_stats(pdf: ProfilePDF, col: ColumnProfile, y: float) -> float:
    _draw_mini_section(pdf, "String Statistics", y)
    y += 8

    stats = [
        ("Min Length", str(col.min_length) if col.min_length is not None else "-"),
        ("Max Length", str(col.max_length) if col.max_length is not None else "-"),
        ("Avg Length", f"{col.avg_length:.1f}" if col.avg_length else "-"),
        ("Empty Strings", f"{col.empty_string_count:,}"),
    ]

    col_w = 42
    for i, (lbl, val) in enumerate(stats):
        _draw_stat_card(pdf, 15 + i * (col_w + 3), y, col_w, 14, lbl, val)

    return y + 22


def _draw_date_stats(pdf: ProfilePDF, col: ColumnProfile, y: float) -> float:
    _draw_mini_section(pdf, "Date Statistics", y)
    y += 8

    stats = [
        ("Earliest", col.min_date or "-"),
        ("Latest", col.max_date or "-"),
        ("Range (days)", str(col.date_range_days) if col.date_range_days is not None else "-"),
    ]

    col_w = 56
    for i, (lbl, val) in enumerate(stats):
        _draw_stat_card(pdf, 15 + i * (col_w + 3), y, col_w, 14, lbl, val[:22])

    return y + 22


def _draw_boolean_stats(pdf: ProfilePDF, col: ColumnProfile, y: float) -> float:
    _draw_mini_section(pdf, "Boolean Distribution", y)
    y += 8

    total = col.true_count + col.false_count
    true_pct = col.true_count / total * 100 if total else 0
    false_pct = col.false_count / total * 100 if total else 0

    stats = [
        ("True", f"{col.true_count:,} ({true_pct:.1f}%)"),
        ("False", f"{col.false_count:,} ({false_pct:.1f}%)"),
    ]

    col_w = 56
    for i, (lbl, val) in enumerate(stats):
        _draw_stat_card(pdf, 15 + i * (col_w + 3), y, col_w, 14, lbl, val)

    # Visual bar
    y += 20
    bar_w = 170
    if total > 0:
        pdf.set_fill_color(*C.GREEN)
        pdf.rect(15, y, bar_w * true_pct / 100, 6, "F")
        pdf.set_fill_color(*C.RED)
        pdf.rect(15 + bar_w * true_pct / 100, y, bar_w * false_pct / 100, 6, "F")
        y += 10

    return y


def _draw_histogram(pdf: ProfilePDF, col: ColumnProfile, y: float) -> float:
    if y > 220:
        pdf.add_page()
        y = pdf.get_y()

    _draw_mini_section(pdf, "Distribution", y)
    y += 8

    max_count = max(h["count"] for h in col.histogram) if col.histogram else 1
    bar_area_w = 170
    bar_h = 50
    num_bars = len(col.histogram)
    bar_w = max(bar_area_w / num_bars - 1, 2)
    gap = max((bar_area_w - bar_w * num_bars) / max(num_bars - 1, 1), 1)

    for i, h in enumerate(col.histogram):
        x = 15 + i * (bar_w + gap)
        pct = h["count"] / max_count if max_count else 0
        bh = max(pct * bar_h, 1)

        # Gradient effect (darker at bottom)
        pdf.set_fill_color(*C.INDIGO)
        pdf.rect(x, y + bar_h - bh, bar_w, bh, "F")

        # Lighter top
        pdf.set_fill_color(*C.INDIGO_LIGHT)
        pdf.rect(x, y + bar_h - bh, bar_w, min(bh, 2), "F")

    # X-axis labels (first and last)
    y += bar_h + 2
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(*C.TEXT_MUTED)

    if col.histogram:
        pdf.set_xy(15, y)
        pdf.cell(40, 4, str(col.histogram[0]["low"]), align="L")
        pdf.set_xy(145, y)
        pdf.cell(40, 4, str(col.histogram[-1]["high"]), align="R")

    return y + 8


def _draw_top_values(pdf: ProfilePDF, col: ColumnProfile, y: float, total_rows: int) -> float:
    if y > 220:
        pdf.add_page()
        y = pdf.get_y()

    _draw_mini_section(pdf, "Top Values", y)
    y += 8

    max_count = col.top_values[0]["count"] if col.top_values else 1

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*C.TEXT_MUTED)

    # Headers
    pdf.set_xy(15, y)
    pdf.cell(70, 5, "VALUE", align="L")
    pdf.cell(25, 5, "COUNT", align="R")
    pdf.cell(20, 5, "%", align="R")
    pdf.cell(50, 5, "", align="L")
    y += 6

    pdf.set_draw_color(*C.BORDER)
    pdf.line(15, y, 185, y)
    y += 2

    pdf.set_font("Helvetica", "", 7.5)
    for tv in col.top_values[:8]:
        if y > 275:
            break
        pdf.set_text_color(*C.TEXT_PRIMARY)
        pdf.set_xy(15, y)
        display_val = tv["value"][:35]
        pdf.cell(70, 5, display_val, align="L")

        pdf.set_text_color(*C.TEXT_SECONDARY)
        pdf.cell(25, 5, f"{tv['count']:,}", align="R")
        pdf.cell(20, 5, f"{tv['pct']:.1f}%", align="R")

        # Mini bar
        bar_x = 135
        bar_max_w = 50
        fill = tv["count"] / max_count * bar_max_w if max_count else 0
        pdf.set_fill_color(*C.BG_STAT)
        pdf.rect(bar_x, y + 1, bar_max_w, 3, "F")
        pdf.set_fill_color(*C.INDIGO)
        pdf.rect(bar_x, y + 1, fill, 3, "F")

        y += 6.5

    return y + 3


# ── Drawing helpers ──────────────────────────────────────────────────────────

def _draw_gradient_rect(pdf: ProfilePDF, x: float, y: float, w: float, h: float):
    """Simulated gradient from indigo to purple."""
    steps = 40
    step_h = h / steps
    for i in range(steps):
        t = i / steps
        r = int(C.INDIGO[0] + (C.PURPLE[0] - C.INDIGO[0]) * t)
        g = int(C.INDIGO[1] + (C.PURPLE[1] - C.INDIGO[1]) * t)
        b = int(C.INDIGO[2] + (C.PURPLE[2] - C.INDIGO[2]) * t)
        pdf.set_fill_color(r, g, b)
        pdf.rect(x, y + i * step_h, w, step_h + 0.5, "F")


def _draw_stat_card(pdf: ProfilePDF, x: float, y: float, w: float, h: float,
                     label: str, value: str):
    pdf.set_fill_color(*C.BG_CARD)
    pdf.rect(x, y, w, h, "F")

    # Top accent line
    pdf.set_fill_color(*C.INDIGO)
    pdf.rect(x, y, w, 1.5, "F")

    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*C.TEXT_MUTED)
    pdf.set_xy(x + 3, y + 3)
    pdf.cell(w - 6, 4, label.upper(), align="L")

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*C.TEXT_PRIMARY)
    pdf.set_xy(x + 3, y + 8)
    pdf.cell(w - 6, 6, value[:16], align="L")


def _draw_section_header(pdf: ProfilePDF, title: str):
    y = pdf.get_y()
    pdf.set_fill_color(*C.INDIGO)
    pdf.rect(15, y, 3, 8, "F")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*C.TEXT_PRIMARY)
    pdf.set_xy(21, y)
    pdf.cell(170, 8, title, align="L")
    pdf.set_y(y + 12)


def _draw_mini_section(pdf: ProfilePDF, title: str, y: float):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*C.INDIGO_LIGHT)
    pdf.set_xy(15, y)
    pdf.cell(170, 5, title, align="L")


def _draw_pdf_progress_bar(pdf: ProfilePDF, x: float, y: float, w: float,
                            label: str, pct: float):
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*C.TEXT_SECONDARY)
    pdf.set_xy(x, y)
    pdf.cell(w, 5, f"{label}: {pct:.1f}%", align="L")

    bar_y = y + 6
    bar_h = 4
    pdf.set_fill_color(*C.BG_STAT)
    pdf.rect(x, bar_y, w, bar_h, "F")

    fc = C.GREEN if pct >= 90 else C.BLUE if pct >= 70 else C.YELLOW if pct >= 50 else C.RED
    pdf.set_fill_color(*fc)
    pdf.rect(x, bar_y, max(w * pct / 100, 0.5), bar_h, "F")


# ── Formatting helpers ───────────────────────────────────────────────────────

def _fmt_num(val) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        if abs(val) >= 1_000_000:
            return f"{val:,.0f}"
        if abs(val) >= 100:
            return f"{val:,.2f}"
        return f"{val:,.4f}"
    return f"{val:,}" if isinstance(val, int) else str(val)


def _fmt_bytes(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"
