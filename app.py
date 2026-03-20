import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAC Q-Commerce Dashboard · Team Real Madrid",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Top header bar */
    .sac-header {
        background: linear-gradient(90deg, #0D1B2A 0%, #162033 100%);
        padding: 14px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .sac-badge {
        background: #0A9396;
        color: white;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 5px;
        letter-spacing: 1px;
    }
    .sac-title {
        color: white;
        font-size: 18px;
        font-weight: 500;
        margin: 0;
    }
    .sac-subtitle {
        color: #94D2BD;
        font-size: 12px;
        margin: 0;
    }

    /* KPI metric cards */
    .kpi-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 16px 18px;
        border-left: 4px solid #0A9396;
        margin-bottom: 8px;
    }
    .kpi-card.warn { border-left-color: #E76F51; }
    .kpi-card.gold { border-left-color: #E9C46A; }

    /* Insight badges */
    .insight-teal {
        display: inline-block;
        background: #E1F5EE;
        color: #0F6E56;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        margin-top: 6px;
    }
    .insight-red {
        display: inline-block;
        background: #FAECE7;
        color: #993C1D;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        margin-top: 6px;
    }
    .insight-gold {
        display: inline-block;
        background: #FAEEDA;
        color: #854F0B;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        margin-top: 6px;
    }

    /* Section card */
    .section-card {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Footer */
    .sac-footer {
        text-align: center;
        color: #6c757d;
        font-size: 11px;
        padding: 12px 0;
        border-top: 1px solid #e9ecef;
        margin-top: 20px;
    }

    /* Streamlit overrides */
    .stMetric {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 12px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 26px !important; }
    div[data-testid="stSidebarContent"] { background: #0D1B2A; }
    section[data-testid="stSidebar"] > div { background: #0D1B2A; }
    section[data-testid="stSidebar"] label { color: #94D2BD !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #94D2BD !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: white !important; }
    section[data-testid="stSidebar"] p { color: #94D2BD !important; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ─────────────────────────────────────────────────────────────
COLORS = {
    "teal":      "#0A9396",
    "teal_lt":   "#94D2BD",
    "navy":      "#0D1B2A",
    "gold":      "#E9C46A",
    "coral":     "#E76F51",
    "green":     "#1D9E75",
    "purple":    "#534AB7",
    "gray":      "#888780",
}
PALETTE = [COLORS["teal"], COLORS["coral"], COLORS["gold"],
           COLORS["navy"], COLORS["green"], COLORS["purple"]]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=11, color="#444"),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

# ── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    from data import get_all_data
    return get_all_data()

data = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 SAC Dashboard")
    st.markdown("**Team Real Madrid**")
    st.markdown("Q-Commerce Behavioral Analytics")
    st.divider()

    st.markdown("### Filters")
    zone = st.selectbox("📍 Location Zone", ["All Zones", "Andheri", "Bandra", "Powai", "Thane", "Dadar"])
    time_window = st.selectbox("⏰ Time Window", [
        "All Windows", "6–9 AM", "9 AM–12", "12–3 PM", "3–6 PM", "6–10 PM", "10 PM–2 AM"
    ])
    category = st.selectbox("📦 Product Category", [
        "All Categories", "Snacks & Beverages", "Fresh Produce", "Dairy",
        "Staples & Grains", "Frozen Foods", "Personal Care"
    ])

    st.divider()
    st.markdown("### SAC Modules Used")
    st.markdown("✅ SAC Modeler")
    st.markdown("✅ SAC Story")
    st.markdown("✅ Smart Predict")
    st.markdown("✅ SAC Planning")
    st.divider()
    st.markdown("📊 **Dataset:** 2,00,000+ records")
    st.markdown("📍 **Zones:** Mumbai — 5 zones")
    st.markdown("🔄 **Last Refresh:** Real-time")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sac-header">
  <div>
    <span class="sac-badge">SAC</span>&nbsp;&nbsp;
    <span class="sac-title">Q-Commerce Behavioral Analytics Dashboard</span>
    <p class="sac-subtitle">Powered by SAP Analytics Cloud · Team Real Madrid · Mumbai Q-Commerce</p>
  </div>
  <div style="color:#94D2BD;font-size:12px;text-align:right">
    200,000+ behavioral records<br>5 Mumbai zones · Live filters active
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Behavioral Overview",
    "🛒 Cart Abandonment",
    "🧠 Smart Predict",
    "🏪 Dark Store Planning"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — BEHAVIORAL OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI Row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Sessions", "1,02,400", "↑ 12% vs last week")
    k2.metric("Avg Cart Value", "₹312", "↑ ₹48 with cross-sell")
    k3.metric("Abandonment Rate", "63%", "↓ Target: <45%", delta_color="inverse")
    k4.metric("Cross-sell Lift", "+₹150", "40% conversion rate")

    st.markdown("---")
    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.markdown("**Order Volume by Time Window & Category** · *SAC Story*")
        fig = go.Figure()
        time_labels = data["time_labels"]
        fig.add_bar(name="Snacks & Beverages", x=time_labels, y=data["snacks"],
                    marker_color=COLORS["teal"], marker_cornerradius=3)
        fig.add_bar(name="Fresh Produce & Dairy", x=time_labels, y=data["fresh"],
                    marker_color=COLORS["coral"], marker_cornerradius=3)
        fig.add_bar(name="Staples & Grains", x=time_labels, y=data["staples"],
                    marker_color=COLORS["gold"], marker_cornerradius=3)
        fig.update_layout(barmode="stack", height=260, **CHART_LAYOUT,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-teal">🌙 Late-night: +45% impulse spike in Snacks & Beverages</span>', unsafe_allow_html=True)

    with c2:
        st.markdown("**Session Duration Distribution** · *SAC Story*")
        dur_labels = ["0–60s", "60–120s", "120–180s", "180–240s", "240s+"]
        dur_vals = [18000, 24000, 22000, 28000, 10000]
        dur_colors = [COLORS["teal"], COLORS["green"], COLORS["gold"], COLORS["coral"], "#993C1D"]
        fig2 = go.Figure(go.Bar(
            x=dur_labels, y=dur_vals,
            marker_color=dur_colors, marker_cornerradius=3
        ))
        fig2.update_layout(height=245, **CHART_LAYOUT,
                           xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">⚠ Sessions >180s carry 70% abandonment risk</span>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Category Share by Order Volume** · *SAC Story*")
        cat_labels = ["Snacks & Bev", "Fresh Produce", "Staples", "Personal Care", "Frozen", "Other"]
        cat_data = [28, 22, 19, 12, 11, 8]
        fig3 = go.Figure(go.Pie(
            labels=cat_labels, values=cat_data,
            hole=0.55, marker_colors=PALETTE,
            textinfo="label+percent", textfont_size=10
        ))
        fig3.update_layout(height=230, **CHART_LAYOUT, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with c4:
        st.markdown("**Cross-sell Conversion by Bundle Pair** · *SAC KPI Tile*")
        cross_labels = ["Snacks + Bev", "Dairy + Breakfast", "Frozen + Snacks", "Grains + Staples", "Personal + Bev"]
        cross_vals = [40, 33, 27, 21, 16]
        fig4 = go.Figure(go.Bar(
            y=cross_labels, x=cross_vals, orientation="h",
            marker_color=[COLORS["teal"], COLORS["green"], COLORS["gold"], COLORS["coral"], "#993C1D"],
            marker_cornerradius=3,
            text=[f"{v}%" for v in cross_vals], textposition="outside"
        ))
        fig4.update_layout(height=230, **CHART_LAYOUT,
                           xaxis=dict(range=[0, 55], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — CART ABANDONMENT
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Fresh Produce Abandon", "58%", "Highest drop-off category", delta_color="inverse")
    k2.metric("Avg Drop-off Session", "194s", "Choice overload zone", delta_color="inverse")
    k3.metric("Recovery Opportunity", "₹38L/mo", "If abandonment → 45%")
    k4.metric("Top Abandon Reason", "Choice Overload", "Staples category")

    st.markdown("---")
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**Conversion Funnel — All Sessions** · *SAC Story*")
        funnel_stages = ["App Sessions", "Product Views", "Add to Cart", "Checkout Start", "Order Complete"]
        funnel_vals = [100000, 72000, 41000, 22000, 14000]
        funnel_pcts = ["100%", "72%", "41%", "22%", "14%"]
        fig5 = go.Figure(go.Funnel(
            y=funnel_stages, x=funnel_vals,
            textinfo="value+percent initial",
            marker=dict(color=[COLORS["navy"], COLORS["teal"], COLORS["green"], COLORS["gold"], COLORS["coral"]]),
            connector=dict(line=dict(color="#ccc", width=1))
        ))
        fig5.update_layout(height=280, **CHART_LAYOUT)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">⚠ 86% of sessions do not result in a completed order</span>', unsafe_allow_html=True)

    with c2:
        st.markdown("**Abandonment Rate by Category** · *SAC Dashboard*")
        ab_cats = ["Fresh Produce", "Dairy", "Staples", "Frozen", "Snacks", "Personal Care"]
        ab_vals = [58, 52, 49, 38, 24, 18]
        ab_colors = [COLORS["coral"] if v > 50 else COLORS["gold"] if v > 35 else COLORS["teal"] for v in ab_vals]
        fig6 = go.Figure(go.Bar(
            y=ab_cats, x=ab_vals, orientation="h",
            marker_color=ab_colors, marker_cornerradius=3,
            text=[f"{v}%" for v in ab_vals], textposition="outside"
        ))
        fig6.update_layout(height=265, **CHART_LAYOUT,
                           xaxis=dict(range=[0, 75], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False))
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-gold">Fresh Produce & Dairy are highest-priority intervention categories</span>', unsafe_allow_html=True)

    st.markdown("**Abandonment Rate by Time Window & Zone** · *SAC Story · Grouped View*")
    zones = ["Andheri", "Bandra", "Powai", "Thane", "Dadar"]
    time_windows = data["time_labels"]
    abandon_matrix = [
        [55, 48, 41, 52, 44],
        [58, 51, 44, 55, 47],
        [61, 54, 47, 58, 50],
        [64, 57, 50, 61, 53],
        [74, 67, 57, 68, 60],
        [69, 62, 52, 65, 57],
    ]
    fig7 = go.Figure()
    bar_colors = [COLORS["navy"], COLORS["teal"], COLORS["green"], COLORS["gold"], COLORS["coral"], "#993C1D"]
    for i, tw in enumerate(time_windows):
        fig7.add_bar(name=tw, x=zones, y=abandon_matrix[i],
                     marker_color=bar_colors[i], marker_cornerradius=2)
    fig7.update_layout(barmode="group", height=220, **CHART_LAYOUT,
                       yaxis=dict(ticksuffix="%", gridcolor="#f0f0f0"),
                       xaxis=dict(showgrid=False))
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — SMART PREDICT
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Model Accuracy", "84%", "Smart Predict classification")
    k2.metric("Top Cross-sell", "Snacks", "72% predicted conversion")
    k3.metric("Churn-Risk Users", "8,240", "Low freq + high recency gap", delta_color="inverse")
    k4.metric("Best Intervention", "10 PM–2 AM", "Highest uplift window")

    st.markdown("---")
    c1, c2 = st.columns([1.1, 1])

    with c1:
        st.markdown("**Predicted Cross-sell Conversion Probability** · *Smart Predict Output*")
        pred_cats = ["Snacks", "Chocolates", "Beverages", "Dairy", "Frozen Foods", "Grains"]
        pred_vals = [72, 68, 58, 44, 31, 22]
        pred_colors = [COLORS["teal"] if v >= 60 else COLORS["gold"] if v >= 40 else COLORS["coral"] for v in pred_vals]
        fig8 = go.Figure(go.Bar(
            y=pred_cats, x=pred_vals, orientation="h",
            marker_color=pred_colors, marker_cornerradius=4,
            text=[f"{v}%" for v in pred_vals], textposition="outside",
            textfont=dict(size=12, color="#333")
        ))
        fig8.update_layout(height=270, **CHART_LAYOUT,
                           xaxis=dict(range=[0, 90], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False, tickfont=dict(size=12)))
        # Add threshold line
        fig8.add_vline(x=50, line_dash="dash", line_color=COLORS["coral"],
                       annotation_text="50% threshold", annotation_position="top")
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-teal">Push Snacks + Chocolates after 10 PM for maximum ROI</span>', unsafe_allow_html=True)

    with c2:
        st.markdown("**Churn Risk Segmentation** · *Smart Predict · Customer Segments*")
        churn_labels = ["Low risk", "Medium risk", "High risk", "At-risk returning"]
        churn_vals = [12, 28, 38, 22]
        fig9 = go.Figure(go.Pie(
            labels=churn_labels, values=churn_vals, hole=0.5,
            marker_colors=[COLORS["teal"], COLORS["gold"], COLORS["coral"], COLORS["purple"]],
            textinfo="label+percent", textfont_size=11,
            pull=[0, 0, 0.08, 0]
        ))
        fig9.update_layout(height=265, **CHART_LAYOUT)
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">38% high-risk segment needs immediate targeted offer</span>', unsafe_allow_html=True)

    st.markdown("**Purchase Intent Score by Time Window** · *Smart Predict · Behavioral Trigger Index*")
    intent_scores = [42, 55, 60, 58, 78, 88]
    fig10 = go.Figure()
    fig10.add_scatter(
        x=data["time_labels"], y=intent_scores,
        mode="lines+markers",
        line=dict(color=COLORS["teal"], width=3),
        fill="tozeroy", fillcolor="rgba(10,147,150,0.12)",
        marker=dict(color=COLORS["teal"], size=8),
        name="Intent Score"
    )
    # Add threshold band
    fig10.add_hrect(y0=75, y1=100, fillcolor="rgba(10,147,150,0.08)",
                    line_width=0, annotation_text="High intent zone",
                    annotation_position="right")
    fig10.update_layout(height=200, **CHART_LAYOUT,
                        yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor="#f0f0f0"),
                        xaxis=dict(showgrid=False),
                        showlegend=False)
    st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})
    st.markdown('<span class="insight-gold">Late-night window has highest purchase intent — prime for predictive push notifications</span>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — DARK STORE PLANNING
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("High Waste Risk Zones", "2 / 5", "Andheri & Thane critical", delta_color="inverse")
    k2.metric("Projected Waste Saving", "30%", "With SAC Planning integrated")
    k3.metric("Fresh Produce Overstock", "₹12.4L/wk", "Current weekly exposure", delta_color="inverse")
    k4.metric("Planning Version", "v3 — Active", "SAC Planning live")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Perishable Waste Risk Score by Zone & Category** · *SAC Planning*")
        zones = ["Andheri", "Bandra", "Powai", "Thane", "Dadar"]
        waste_fresh = [82, 65, 48, 71, 55]
        waste_dairy = [68, 52, 38, 62, 45]
        fig11 = go.Figure()
        fig11.add_bar(name="Fresh Produce", y=zones, x=waste_fresh, orientation="h",
                      marker_color=COLORS["coral"], marker_cornerradius=3)
        fig11.add_bar(name="Dairy", y=zones, x=waste_dairy, orientation="h",
                      marker_color=COLORS["gold"], marker_cornerradius=3)
        fig11.add_vline(x=60, line_dash="dash", line_color="#aaa",
                        annotation_text="Action threshold (60)",
                        annotation_position="top right", annotation_font_size=10)
        fig11.update_layout(barmode="group", height=270, **CHART_LAYOUT,
                            xaxis=dict(range=[0, 100], showgrid=False),
                            yaxis=dict(showgrid=False))
        st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">Andheri & Thane exceed action threshold — procurement adjustment required</span>', unsafe_allow_html=True)

    with c2:
        st.markdown("**Dark Store Inventory vs SAC Demand Forecast** · *SAC Planning*")
        inv_zones = ["Andheri", "Bandra", "Powai", "Thane", "Dadar"]
        inv_stock = [100, 100, 100, 100, 100]
        inv_demand = [60, 88, 93, 72, 80]
        fig12 = go.Figure()
        fig12.add_bar(name="Current Stock Level (index)", x=inv_zones, y=inv_stock,
                      marker_color=COLORS["navy"], marker_cornerradius=3, opacity=0.7)
        fig12.add_bar(name="SAC Demand Forecast (index)", x=inv_zones, y=inv_demand,
                      marker_color=COLORS["teal"], marker_cornerradius=3)
        fig12.update_layout(barmode="group", height=260, **CHART_LAYOUT,
                            yaxis=dict(ticksuffix=" idx", gridcolor="#f0f0f0"),
                            xaxis=dict(showgrid=False))
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">Andheri: 40% overstock vs forecasted behavioral demand</span>', unsafe_allow_html=True)

    st.markdown("**Procurement Adjustment Recommendations by Zone** · *SAC Planning · Action Trigger*")
    recs = {
        "Zone": ["Andheri", "Bandra", "Powai", "Thane", "Dadar"],
        "Waste Risk": ["🔴 High (82)", "🟡 Medium (65)", "🟢 Low (48)", "🔴 High (71)", "🟡 Medium (55)"],
        "Recommended Action": [
            "Reduce Fresh Produce by 35%",
            "Increase Snacks stock by 12%",
            "Maintain current levels",
            "Reduce Dairy by 28%",
            "Reduce Fresh Produce by 20%"
        ],
        "SAC Confidence": ["94%", "87%", "91%", "89%", "85%"],
        "Est. Weekly Saving": ["₹3.2L", "—", "—", "₹2.8L", "₹1.6L"],
        "Priority": ["URGENT", "MODERATE", "STABLE", "URGENT", "MODERATE"]
    }
    df_recs = pd.DataFrame(recs)

    def style_priority(val):
        if val == "URGENT":
            return "background-color: #FAECE7; color: #993C1D; font-weight: 600"
        elif val == "MODERATE":
            return "background-color: #FAEEDA; color: #854F0B; font-weight: 600"
        else:
            return "background-color: #E1F5EE; color: #0F6E56; font-weight: 600"

    styled_df = df_recs.style.applymap(style_priority, subset=["Priority"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=215)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sac-footer">
    SAP Analytics Cloud &nbsp;·&nbsp; Q-Commerce Behavioral Dataset &nbsp;·&nbsp;
    2,00,000+ records &nbsp;·&nbsp; Mumbai Zones &nbsp;·&nbsp;
    <strong>Team Real Madrid</strong> &nbsp;·&nbsp; University Presentation 2025
</div>
""", unsafe_allow_html=True)
