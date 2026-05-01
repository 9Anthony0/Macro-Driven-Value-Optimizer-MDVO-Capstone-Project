"""styles.py — Institutional-grade CSS for MDVO tabbed dashboard."""

CUSTOM_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Foundation ── */
.stApp {
    background: #101318;
    font-family: 'Inter', -apple-system, sans-serif;
    color: #c8cdd5;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13161d 0%, #111419 100%) !important;
    border-right: 1px solid #1e2229;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    color: #e4e8ee; font-size: 1rem; letter-spacing: .03em;
}

/* ── Metrics — raised panel style ── */
div[data-testid="stMetric"] {
    background: #181c24;
    border: 1px solid #22272f;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.25), 0 0 0 1px rgba(255,255,255,.02);
}
div[data-testid="stMetric"] label {
    color: #6b7280 !important;
    font-size: .65rem !important;
    text-transform: uppercase;
    letter-spacing: .14em;
    font-weight: 600;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700;
    font-size: 1.35rem !important;
    color: #e4e8ee !important;
}

/* ── Typography ── */
h1 { color: #f0f2f5 !important; font-weight: 800 !important; font-size: 1.8rem !important; letter-spacing: -.01em; }
h3 { color: #d1d5db !important; font-weight: 600 !important; font-size: 1.05rem !important; }
h4 { color: #9ca3af !important; font-weight: 600 !important; font-size: .9rem !important; }

/* ── Tabs — refined ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: #14171e; border-radius: 10px; padding: 3px;
    border: 1px solid #1e2229;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #6b7280; font-weight: 500;
    font-size: .82rem; padding: 8px 20px;
    transition: all .15s ease;
}
.stTabs [aria-selected="true"] {
    background: #1f2937 !important; color: #f0f2f5 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.3);
}

/* ── DataFrames ── */
div[data-testid="stDataFrame"] {
    border-radius: 10px; overflow: hidden;
    border: 1px solid #1e2229;
    box-shadow: 0 2px 8px rgba(0,0,0,.2);
}

/* ── Panels ── */
.panel {
    background: #181c24;
    border: 1px solid #22272f;
    border-radius: 14px;
    padding: 24px 28px;
    margin: 8px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,.2), inset 0 1px 0 rgba(255,255,255,.02);
}
.panel-header {
    font-size: .68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .14em;
    color: #6b7280;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #22272f;
}

/* ── Accent pills ── */
.pill {
    display: inline-block; padding: 4px 14px; border-radius: 6px;
    font-size: .68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; margin-bottom: 8px;
}
.p-blue { background: rgba(59,130,246,.1); color: #60a5fa; border: 1px solid rgba(59,130,246,.2); }
.p-green { background: rgba(16,185,129,.1); color: #34d399; border: 1px solid rgba(16,185,129,.2); }
.p-purple { background: rgba(139,92,246,.1); color: #a78bfa; border: 1px solid rgba(139,92,246,.2); }
.p-amber { background: rgba(245,158,11,.1); color: #fbbf24; border: 1px solid rgba(245,158,11,.2); }
.p-red { background: rgba(239,68,68,.1); color: #f87171; border: 1px solid rgba(239,68,68,.2); }

/* ── Dividers ── */
.sep { height: 1px; background: #22272f; margin: 24px 0; }

/* ── Sidebar cards ── */
.sidebar-card {
    background: #181c24;
    border: 1px solid #22272f;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 6px 0;
}
</style>"""

# Chart template for consistent Plotly styling
CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color="#9ca3af", size=11),
    margin=dict(l=48, r=24, t=48, b=40),
    xaxis=dict(gridcolor="#1e2229", zerolinecolor="#22272f"),
    yaxis=dict(gridcolor="#1e2229", zerolinecolor="#22272f"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
)

SECTOR_COLORS = {
    "Technology": "#3b82f6",
    "Consumer Discretionary": "#f59e0b",
    "Consumer Staples": "#10b981",
    "Energy": "#ef4444",
    "Healthcare": "#8b5cf6",
    "Financials": "#06b6d4",
    "Communication Services": "#fbbf24",
    "Other": "#6b7280",
}
