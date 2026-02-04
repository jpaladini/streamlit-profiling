"""Custom CSS styles for the Snowflake Data Profiler."""

MAIN_CSS = """
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ── Header ── */
    .app-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    .app-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    .app-header h1 {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.25rem !important;
        letter-spacing: -0.02em;
    }

    .app-header p {
        color: rgba(255,255,255,0.85) !important;
        font-size: 1.05rem !important;
        font-weight: 400;
        margin: 0 !important;
    }

    /* ── Metric Cards ── */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .metric-card {
        background: linear-gradient(145deg, #1E293B 0%, #1a2332 100%);
        border: 1px solid rgba(79, 70, 229, 0.2);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        flex: 1;
        min-width: 160px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(79, 70, 229, 0.5);
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }

    .metric-card:nth-child(1)::after { background: linear-gradient(90deg, #4F46E5, #7C3AED); }
    .metric-card:nth-child(2)::after { background: linear-gradient(90deg, #06B6D4, #3B82F6); }
    .metric-card:nth-child(3)::after { background: linear-gradient(90deg, #10B981, #34D399); }
    .metric-card:nth-child(4)::after { background: linear-gradient(90deg, #F59E0B, #EF4444); }
    .metric-card:nth-child(5)::after { background: linear-gradient(90deg, #EC4899, #8B5CF6); }
    .metric-card:nth-child(6)::after { background: linear-gradient(90deg, #14B8A6, #06B6D4); }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #F1F5F9;
        line-height: 1.2;
    }

    .metric-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.2rem;
    }

    /* ── Quality Score ── */
    .quality-score-container {
        background: linear-gradient(145deg, #1E293B 0%, #1a2332 100%);
        border: 1px solid rgba(79, 70, 229, 0.2);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .quality-ring {
        width: 160px;
        height: 160px;
        margin: 0 auto 1rem auto;
        position: relative;
    }

    .quality-score-value {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
    }

    .quality-score-label {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 500;
    }

    .quality-excellent { color: #10B981; }
    .quality-good { color: #3B82F6; }
    .quality-fair { color: #F59E0B; }
    .quality-poor { color: #EF4444; }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
    }

    .section-header h2 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #F1F5F9 !important;
        margin: 0 !important;
    }

    .section-badge {
        background: rgba(79, 70, 229, 0.15);
        color: #818CF8;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        border: 1px solid rgba(79, 70, 229, 0.3);
    }

    /* ── Column Cards ── */
    .column-card {
        background: linear-gradient(145deg, #1E293B 0%, #1a2332 100%);
        border: 1px solid rgba(79, 70, 229, 0.15);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s ease;
    }

    .column-card:hover {
        border-color: rgba(79, 70, 229, 0.4);
    }

    .column-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .column-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #E2E8F0;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }

    .column-type-badge {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .type-numeric {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .type-string {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .type-date {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .type-boolean {
        background: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }

    .type-other {
        background: rgba(148, 163, 184, 0.15);
        color: #94A3B8;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* ── Stat Grid ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 0.75rem;
    }

    .stat-item {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        padding: 0.75rem;
        border: 1px solid rgba(51, 65, 85, 0.5);
    }

    .stat-item-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }

    .stat-item-value {
        font-size: 1rem;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* ── Progress Bars (Completeness / Uniqueness) ── */
    .progress-container {
        margin: 0.75rem 0;
    }

    .progress-label-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
    }

    .progress-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
    }

    .progress-value {
        font-size: 0.75rem;
        font-weight: 700;
        color: #E2E8F0;
    }

    .progress-bar-bg {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
    }

    .progress-bar-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease;
    }

    .fill-green { background: linear-gradient(90deg, #10B981, #34D399); }
    .fill-blue { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
    .fill-yellow { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
    .fill-red { background: linear-gradient(90deg, #EF4444, #F87171); }
    .fill-purple { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }

    /* ── Top Values Table ── */
    .top-values-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 0.75rem;
    }

    .top-values-table th {
        font-size: 0.7rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 0.5rem 0.75rem;
        text-align: left;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
    }

    .top-values-table td {
        font-size: 0.85rem;
        color: #CBD5E1;
        padding: 0.4rem 0.75rem;
        border-bottom: 1px solid rgba(51, 65, 85, 0.2);
    }

    .top-values-table tr:last-child td {
        border-bottom: none;
    }

    .top-values-table .bar-cell {
        width: 40%;
    }

    .mini-bar-bg {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 4px;
        height: 6px;
        overflow: hidden;
    }

    .mini-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #0B1120;
        border-right: 1px solid rgba(79, 70, 229, 0.15);
    }

    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background: #1E293B;
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 8px;
        color: #E2E8F0;
    }

    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #1E293B;
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 8px;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.2s ease;
    }

    .stButton > button:first-child {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.6rem 1.5rem !important;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: #94A3B8;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(79, 70, 229, 0.15) !important;
        color: #818CF8 !important;
        border-bottom: 2px solid #4F46E5 !important;
    }

    /* ── Expanders ── */
    .streamlit-expanderHeader {
        background: #1E293B;
        border-radius: 10px;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #4F46E5 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(51, 65, 85, 0.3) !important;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #64748B;
    }

    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .empty-state h3 {
        color: #94A3B8 !important;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* ── Connection status ── */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .status-connected {
        background: rgba(16, 185, 129, 0.1);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-disconnected {
        background: rgba(239, 68, 68, 0.1);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }

    .dot-green { background: #10B981; box-shadow: 0 0 6px rgba(16,185,129,0.5); }
    .dot-red { background: #EF4444; box-shadow: 0 0 6px rgba(239,68,68,0.5); }

    /* ── Sidebar logo area ── */
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(79, 70, 229, 0.15);
        margin-bottom: 1.5rem;
    }

    .sidebar-logo h2 {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #E2E8F0 !important;
        margin: 0 !important;
    }

    .sidebar-logo p {
        font-size: 0.75rem;
        color: #64748B;
        margin: 0.25rem 0 0 0;
    }

    /* ── Hide Streamlit elements ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""


def get_quality_color_class(score: float) -> str:
    if score >= 90:
        return "quality-excellent"
    elif score >= 70:
        return "quality-good"
    elif score >= 50:
        return "quality-fair"
    return "quality-poor"


def get_quality_label(score: float) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    return "Needs Attention"


def get_progress_fill_class(pct: float) -> str:
    if pct >= 90:
        return "fill-green"
    elif pct >= 70:
        return "fill-blue"
    elif pct >= 50:
        return "fill-yellow"
    return "fill-red"


def render_metric_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """


def render_progress_bar(label: str, pct: float, fill_class: str = "") -> str:
    if not fill_class:
        fill_class = get_progress_fill_class(pct)
    return f"""
    <div class="progress-container">
        <div class="progress-label-row">
            <span class="progress-label">{label}</span>
            <span class="progress-value">{pct:.1f}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill {fill_class}" style="width: {min(pct, 100):.1f}%"></div>
        </div>
    </div>
    """


def render_stat_item(label: str, value: str) -> str:
    return f"""
    <div class="stat-item">
        <div class="stat-item-label">{label}</div>
        <div class="stat-item-value">{value}</div>
    </div>
    """
