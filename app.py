"""Snowflake Data Profiler — Streamlit application for profiling
Snowflake tables and views with PDF export.

Runs natively in Streamlit in Snowflake (SiS) via get_active_session().
When no Snowflake session is available, falls back to preview mode
with realistic mock data so the layout can be viewed anywhere.
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go

from profiler import TableProfile, ColumnProfile
from pdf_export import generate_pdf
from styles import (
    MAIN_CSS,
    get_quality_color_class,
    get_quality_label,
    render_metric_card,
    render_progress_bar,
    render_stat_item,
)

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Snowflake Data Profiler",
    page_icon="snowflake",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Detect environment ──────────────────────────────────────────────────────

def _try_get_session():
    """Try to get a Snowpark active session. Returns (session, profiler) or (None, None)."""
    try:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
        # Verify the session actually works by running a trivial query
        session.sql("SELECT 1").collect()
        from profiler import SnowflakeProfiler
        return session, SnowflakeProfiler(session)
    except Exception:
        return None, None


@st.cache_resource
def init_session():
    return _try_get_session()


_session, _profiler = init_session()
_HAS_SESSION = _session is not None

if "profile" not in st.session_state:
    st.session_state.profile = None
if "force_preview" not in st.session_state:
    st.session_state.force_preview = not _HAS_SESSION


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">'
        "<h2>Snowflake Data Profiler</h2>"
        "<p>Table & View Analysis</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Preview toggle — always visible
    preview_on = st.toggle(
        "Preview mode (sample data)",
        value=st.session_state.force_preview,
        help="Show the app with mock data. Turn off when connected to Snowflake.",
    )
    st.session_state.force_preview = preview_on

    # If user forced preview, or we have no session → preview mode
    st.session_state.live_mode = _HAS_SESSION and not preview_on

    if st.session_state.live_mode:
        # ── Connected: full interactive sidebar ──────────────────────────
        st.markdown(
            '<div class="connection-status status-connected">'
            '<span class="status-dot dot-green"></span> Connected (active session)'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Select Object")

        databases = _profiler.list_databases()
        database = st.selectbox("Database", databases, index=None, placeholder="Select database...")

        schemas: list[str] = []
        schema = None
        if database:
            schemas = _profiler.list_schemas(database)
            schema = st.selectbox("Schema", schemas, index=None, placeholder="Select schema...")

        tables: list[dict] = []
        selected_table = None
        if database and schema:
            tables = _profiler.list_tables(database, schema)
            table_options = [
                f"{'[VIEW] ' if t['TABLE_TYPE'] == 'VIEW' else ''}{t['TABLE_NAME']}"
                for t in tables
            ]
            selected_idx = st.selectbox(
                "Table / View",
                range(len(table_options)),
                format_func=lambda i: table_options[i],
                index=None,
                placeholder="Select table...",
            )
            if selected_idx is not None:
                selected_table = tables[selected_idx]

        if selected_table:
            st.markdown("---")
            st.markdown("#### Options")
            use_sample = st.checkbox("Sample rows (faster)", value=False)
            sample_size = None
            if use_sample:
                sample_size = st.number_input("Sample size", 1000, 1_000_000, 100_000, step=10_000)

            profile_clicked = st.button(
                "Profile Table",
                use_container_width=True,
                type="primary",
            )

            if profile_clicked:
                with st.spinner(""):
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()

                    def on_progress(current: int, total: int, col_name: str):
                        pct = current / total
                        progress_bar.progress(pct)
                        status_text.markdown(
                            f"<small style='color:#94A3B8'>Profiling column {current}/{total}: "
                            f"<code>{col_name}</code></small>",
                            unsafe_allow_html=True,
                        )

                    profile = _profiler.profile_table(
                        database=database,
                        schema=schema,
                        table=selected_table["TABLE_NAME"],
                        table_type=selected_table["TABLE_TYPE"],
                        sample_size=sample_size,
                        progress_callback=on_progress,
                    )
                    st.session_state.profile = profile
                    progress_bar.empty()
                    status_text.empty()
                    st.rerun()

    else:
        # ── Preview mode: greyed-out controls + demo data ────────────────
        st.markdown(
            '<div class="connection-status status-disconnected">'
            '<span class="status-dot dot-red"></span> Preview Mode'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); '
            'border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem; font-size: 0.82rem; color: #FBBF24;">'
            "No Snowflake session detected. Showing preview with sample data. "
            "Deploy to Streamlit in Snowflake for live profiling."
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Select Object")
        st.selectbox("Database", ["ANALYTICS"], disabled=True)
        st.selectbox("Schema", ["PUBLIC"], disabled=True)
        st.selectbox("Table / View", ["ORDERS"], disabled=True)

        st.markdown("---")
        st.markdown("#### Options")
        st.checkbox("Sample rows (faster)", value=False, disabled=True)
        st.button("Profile Table", use_container_width=True, type="primary", disabled=True)

        # Load mock data automatically in preview mode
        from mock_data import generate_mock_profile
        st.session_state.profile = generate_mock_profile()


# ── Main area ────────────────────────────────────────────────────────────────

def main_content():
    profile: TableProfile | None = st.session_state.profile

    if profile is None:
        _render_empty_state()
        return

    # Preview banner
    if not st.session_state.get("live_mode", False):
        st.markdown(
            '<div style="background: linear-gradient(90deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05)); '
            'border: 1px solid rgba(245,158,11,0.25); border-radius: 10px; padding: 0.75rem 1.25rem; '
            'margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">'
            '<span style="font-size: 1.25rem;">&#x1F441;</span>'
            '<div>'
            '<span style="color: #FBBF24; font-weight: 600; font-size: 0.9rem;">Preview Mode</span>'
            '<span style="color: #94A3B8; font-size: 0.82rem;"> &mdash; '
            "Viewing sample data from a fictional ORDERS table. "
            "Deploy to Streamlit in Snowflake to profile your own tables.</span>"
            "</div></div>",
            unsafe_allow_html=True,
        )

    _render_header(profile)
    _render_overview_metrics(profile)

    tab_overview, tab_columns, tab_quality, tab_warnings = st.tabs(
        ["Overview", "Column Details", "Quality", "Warnings"]
    )

    with tab_overview:
        _render_overview_tab(profile)

    with tab_columns:
        _render_columns_tab(profile)

    with tab_quality:
        _render_quality_tab(profile)

    with tab_warnings:
        _render_warnings_tab(profile)


# ── Empty state ──────────────────────────────────────────────────────────────

def _render_empty_state():
    st.markdown(
        '<div class="app-header">'
        "<h1>Snowflake Data Profiler</h1>"
        "<p>Select a table or view from the sidebar to generate a detailed profile.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-state-icon">&#x2744;</div>'
        "<h3>No profile loaded</h3>"
        "<p>Choose a database, schema, and table, then click <strong>Profile Table</strong>.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Header ───────────────────────────────────────────────────────────────────

def _render_header(p: TableProfile):
    type_label = "VIEW" if p.table_type == "VIEW" else "TABLE"
    st.markdown(
        f'<div class="app-header">'
        f"<h1>{p.table_name}</h1>"
        f"<p>{p.database}.{p.schema} &nbsp;&bull;&nbsp; {type_label} "
        f"&nbsp;&bull;&nbsp; Profiled {p.profiled_at[:19].replace('T', ' ')}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([6, 2, 2])
    with col3:
        pdf_bytes = generate_pdf(p)
        st.download_button(
            label="Export PDF Report",
            data=pdf_bytes,
            file_name=f"profile_{p.table_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ── Overview metrics row ────────────────────────────────────────────────────

def _render_overview_metrics(p: TableProfile):
    size_str = _fmt_bytes(p.size_bytes) if p.size_bytes else "N/A"
    cards_html = '<div class="metric-row">'
    cards_html += render_metric_card("Total Rows", f"{p.row_count:,}")
    cards_html += render_metric_card("Columns", str(p.column_count))
    cards_html += render_metric_card("Completeness", f"{p.overall_completeness:.1f}%")
    cards_html += render_metric_card("Uniqueness", f"{p.overall_uniqueness:.1f}%")
    cards_html += render_metric_card("Quality Score", f"{p.quality_score:.0f}/100")
    cards_html += render_metric_card("Size", size_str)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


# ── Overview tab ─────────────────────────────────────────────────────────────

def _render_overview_tab(p: TableProfile):
    st.markdown(
        '<div class="section-header">'
        "<h2>Column Summary</h2>"
        f'<span class="section-badge">{p.column_count} columns</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    type_counts: dict[str, int] = {}
    for c in p.columns:
        type_counts[c.type_category] = type_counts.get(c.type_category, 0) + 1

    type_colors_map = {
        "numeric": "#3B82F6",
        "string": "#10B981",
        "date": "#F59E0B",
        "boolean": "#8B5CF6",
        "other": "#64748B",
    }

    col1, col2 = st.columns([1, 2])

    with col1:
        fig = go.Figure(
            go.Pie(
                labels=list(type_counts.keys()),
                values=list(type_counts.values()),
                hole=0.6,
                marker_colors=[type_colors_map.get(t, "#64748B") for t in type_counts],
                textinfo="label+value",
                textfont=dict(size=12, color="#E2E8F0"),
            )
        )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=220,
            annotations=[
                dict(
                    text=f"{p.column_count}",
                    x=0.5, y=0.55,
                    font_size=28, font_color="#E2E8F0", font_family="Inter",
                    showarrow=False, font_weight=700,
                ),
                dict(
                    text="columns",
                    x=0.5, y=0.4,
                    font_size=11, font_color="#94A3B8", font_family="Inter",
                    showarrow=False,
                ),
            ],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        col_names = [c.name for c in p.columns]
        completeness = [c.completeness_pct for c in p.columns]
        colors = [
            "#10B981" if v >= 90 else "#3B82F6" if v >= 70 else "#F59E0B" if v >= 50 else "#EF4444"
            for v in completeness
        ]

        fig = go.Figure(
            go.Bar(
                x=completeness,
                y=col_names,
                orientation="h",
                marker_color=colors,
                text=[f"{v:.0f}%" for v in completeness],
                textposition="inside",
                textfont=dict(size=10, color="white"),
            )
        )
        fig.update_layout(
            title=dict(text="Completeness by Column", font=dict(size=13, color="#94A3B8")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                range=[0, 105],
                showgrid=False,
                tickfont=dict(color="#64748B"),
                title="",
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(color="#CBD5E1", size=10),
                title="",
            ),
            margin=dict(l=10, r=10, t=35, b=10),
            height=max(220, len(col_names) * 26),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Columns tab ──────────────────────────────────────────────────────────────

def _render_columns_tab(p: TableProfile):
    search = st.text_input("Search columns", placeholder="Filter by name or type...")
    cols = p.columns
    if search:
        q = search.lower()
        cols = [c for c in cols if q in c.name.lower() or q in c.data_type.lower() or q in c.type_category]

    for col in cols:
        _render_column_card(col, p.row_count)


def _render_column_card(col: ColumnProfile, total_rows: int):
    type_class = f"type-{col.type_category}"

    header_html = (
        f'<div class="column-card"><div class="column-card-header">'
        f'<span class="column-name">{col.name}</span>'
        f'<span class="column-type-badge {type_class}">{col.data_type}</span>'
        f"</div>"
    )

    header_html += render_progress_bar("Completeness", col.completeness_pct)
    header_html += render_progress_bar("Uniqueness", col.uniqueness_pct, "fill-purple")

    header_html += '<div class="stat-grid">'
    header_html += render_stat_item("Total", f"{col.total_count:,}")
    header_html += render_stat_item("Non-Null", f"{col.non_null_count:,}")
    header_html += render_stat_item("Null", f"{col.null_count:,}")
    header_html += render_stat_item("Distinct", f"{col.distinct_count:,}")

    if col.type_category == "numeric":
        header_html += render_stat_item("Min", _fmt(col.min_value))
        header_html += render_stat_item("Max", _fmt(col.max_value))
        header_html += render_stat_item("Mean", _fmt(col.mean_value))
        header_html += render_stat_item("Median", _fmt(col.median_value))
        header_html += render_stat_item("Std Dev", _fmt(col.stddev_value))
        header_html += render_stat_item("P25", _fmt(col.p25))
        header_html += render_stat_item("P75", _fmt(col.p75))
        header_html += render_stat_item("Sum", _fmt(col.sum_value))
    elif col.type_category == "string":
        header_html += render_stat_item("Min Len", _fmt(col.min_length))
        header_html += render_stat_item("Max Len", _fmt(col.max_length))
        header_html += render_stat_item("Avg Len", _fmt(col.avg_length))
        header_html += render_stat_item("Empty", f"{col.empty_string_count:,}")
    elif col.type_category == "date":
        header_html += render_stat_item("Earliest", str(col.min_date or "-")[:10])
        header_html += render_stat_item("Latest", str(col.max_date or "-")[:10])
        header_html += render_stat_item("Range", f"{col.date_range_days or 0:,} days")
    elif col.type_category == "boolean":
        header_html += render_stat_item("True", f"{col.true_count:,}")
        header_html += render_stat_item("False", f"{col.false_count:,}")

    header_html += "</div>"

    if col.top_values:
        max_count = col.top_values[0]["count"] if col.top_values else 1
        header_html += '<table class="top-values-table"><thead><tr>'
        header_html += "<th>Top Values</th><th>Count</th><th>%</th><th class='bar-cell'>Distribution</th>"
        header_html += "</tr></thead><tbody>"
        for tv in col.top_values[:6]:
            bar_pct = tv["count"] / max_count * 100 if max_count else 0
            val_display = tv["value"][:40]
            header_html += (
                f"<tr><td>{val_display}</td>"
                f"<td>{tv['count']:,}</td>"
                f"<td>{tv['pct']:.1f}%</td>"
                f'<td class="bar-cell"><div class="mini-bar-bg">'
                f'<div class="mini-bar-fill" style="width:{bar_pct:.1f}%"></div>'
                f"</div></td></tr>"
            )
        header_html += "</tbody></table>"

    header_html += "</div>"

    st.markdown(header_html, unsafe_allow_html=True)

    if col.type_category == "numeric" and col.histogram:
        fig = go.Figure(
            go.Bar(
                x=[h["low"] for h in col.histogram],
                y=[h["count"] for h in col.histogram],
                marker=dict(
                    color=[h["count"] for h in col.histogram],
                    colorscale=[[0, "#4F46E5"], [1, "#7C3AED"]],
                ),
                width=[(h["high"] - h["low"]) * 0.9 for h in col.histogram],
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(color="#64748B", size=9), title=""),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(51,65,85,0.3)",
                tickfont=dict(color="#64748B", size=9),
                title="",
            ),
            margin=dict(l=40, r=10, t=10, b=30),
            height=180,
            bargap=0.05,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if col.type_category == "boolean" and col.non_null_count > 0:
        fig = go.Figure(
            go.Pie(
                labels=["True", "False"],
                values=[col.true_count, col.false_count],
                hole=0.55,
                marker_colors=["#10B981", "#EF4444"],
                textinfo="label+percent",
                textfont=dict(size=12, color="#E2E8F0"),
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=180,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Quality tab ──────────────────────────────────────────────────────────────

def _render_quality_tab(p: TableProfile):
    score = p.quality_score
    color_class = get_quality_color_class(score)
    label = get_quality_label(score)

    col1, col2 = st.columns([1, 2])

    with col1:
        color_map = {
            "quality-excellent": "#10B981",
            "quality-good": "#3B82F6",
            "quality-fair": "#F59E0B",
            "quality-poor": "#EF4444",
        }
        gauge_color = color_map.get(color_class, "#3B82F6")

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score,
                number=dict(
                    font=dict(size=48, color="#E2E8F0", family="Inter"),
                    suffix="",
                ),
                gauge=dict(
                    axis=dict(range=[0, 100], visible=False),
                    bar=dict(color=gauge_color, thickness=0.7),
                    bgcolor="rgba(30,41,59,0.5)",
                    borderwidth=0,
                    shape="angular",
                ),
                title=dict(text=label, font=dict(size=16, color=gauge_color)),
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=30, r=30, t=60, b=20),
            height=250,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown(
            '<div class="section-header"><h2>Quality Breakdown</h2></div>',
            unsafe_allow_html=True,
        )

        quality_html = ""
        for col in p.columns:
            quality_html += render_progress_bar(
                f"{col.name} — completeness",
                col.completeness_pct,
            )
        st.markdown(f'<div class="column-card">{quality_html}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header"><h2>Completeness vs Uniqueness</h2></div>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    for col in p.columns:
        tc = {
            "numeric": "#3B82F6",
            "string": "#10B981",
            "date": "#F59E0B",
            "boolean": "#8B5CF6",
        }.get(col.type_category, "#64748B")

        fig.add_trace(
            go.Scatter(
                x=[col.completeness_pct],
                y=[col.uniqueness_pct],
                mode="markers+text",
                text=[col.name],
                textposition="top center",
                textfont=dict(size=9, color="#94A3B8"),
                marker=dict(size=12, color=tc, opacity=0.85, line=dict(width=1, color="white")),
                name=col.name,
                showlegend=False,
            )
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            title="Completeness %",
            range=[-5, 110],
            showgrid=True,
            gridcolor="rgba(51,65,85,0.3)",
            tickfont=dict(color="#64748B"),
            titlefont=dict(color="#94A3B8"),
        ),
        yaxis=dict(
            title="Uniqueness %",
            range=[-5, 110],
            showgrid=True,
            gridcolor="rgba(51,65,85,0.3)",
            tickfont=dict(color="#64748B"),
            titlefont=dict(color="#94A3B8"),
        ),
        margin=dict(l=50, r=20, t=20, b=50),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Warnings tab ─────────────────────────────────────────────────────────────

def _render_warnings_tab(p: TableProfile):
    if not p.warnings:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">&#x2705;</div>'
            "<h3>No warnings</h3>"
            "<p>All columns look healthy.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="section-header">'
        f"<h2>Warnings</h2>"
        f'<span class="section-badge">{len(p.warnings)} issues</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    for w in p.warnings:
        severity_color = "#F59E0B"
        if "empty" in w.lower() or "50%" in w:
            severity_color = "#EF4444"
        elif "unique" in w.lower() or "single" in w.lower():
            severity_color = "#3B82F6"

        st.markdown(
            f'<div class="column-card" style="border-left: 3px solid {severity_color}; padding: 0.75rem 1.25rem;">'
            f'<span style="color: {severity_color}; font-weight: 600; margin-right: 0.5rem;">&#x26A0;</span>'
            f'<span style="color: #CBD5E1;">{w}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fmt(val) -> str:
    if val is None:
        return "-"
    if isinstance(val, float):
        if abs(val) >= 1_000_000:
            return f"{val:,.0f}"
        if abs(val) >= 100:
            return f"{val:,.2f}"
        return f"{val:,.4f}"
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)


def _fmt_bytes(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


# ── Run ──────────────────────────────────────────────────────────────────────

main_content()
