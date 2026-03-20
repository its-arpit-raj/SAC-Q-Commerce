import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="SAC Q-Commerce Dashboard · Team Real Madrid",
    page_icon="🛒", layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── KPI cards ── */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.kpi-card{background:#0D1B2A;border-radius:12px;padding:18px 20px;border-left:4px solid #0A9396;position:relative}
.kpi-card.warn{border-left-color:#E76F51}
.kpi-card.gold{border-left-color:#E9C46A}
.kpi-card.green{border-left-color:#1D9E75}
.kpi-label{font-size:11px;font-weight:600;color:#94D2BD;letter-spacing:.8px;text-transform:uppercase;margin-bottom:8px}
.kpi-value{font-size:32px;font-weight:700;color:#FFFFFF;line-height:1.1;margin-bottom:6px}
.kpi-delta{font-size:12px;font-weight:500;padding:3px 8px;border-radius:10px;display:inline-block}
.kpi-delta.up{background:rgba(29,158,117,0.2);color:#5EEAD4}
.kpi-delta.down{background:rgba(231,111,81,0.2);color:#FCA5A5}
.kpi-delta.neutral{background:rgba(148,210,189,0.15);color:#94D2BD}

/* ── Insight badges ── */
.insight-teal{display:inline-block;background:#0F3D3E;color:#5EEAD4;font-size:12px;font-weight:500;padding:5px 12px;border-radius:12px;margin-top:8px;border:1px solid #0A9396}
.insight-red{display:inline-block;background:#3D1515;color:#FCA5A5;font-size:12px;font-weight:500;padding:5px 12px;border-radius:12px;margin-top:8px;border:1px solid #E76F51}
.insight-gold{display:inline-block;background:#3D2E0A;color:#FCD34D;font-size:12px;font-weight:500;padding:5px 12px;border-radius:12px;margin-top:8px;border:1px solid #E9C46A}

/* ── Header ── */
.sac-header{background:#0D1B2A;padding:14px 22px;border-radius:10px;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between}
.sac-badge{background:#0A9396;color:#fff;font-size:11px;font-weight:700;padding:4px 10px;border-radius:5px;letter-spacing:1px}
.sac-title{color:#fff;font-size:17px;font-weight:600;margin:0}
.sac-subtitle{color:#94D2BD;font-size:11px;margin:3px 0 0 0}

/* ── Sidebar ── */
section[data-testid="stSidebar"]>div{background:#0D1B2A!important}
section[data-testid="stSidebar"] *{color:#94D2BD!important}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] strong{color:#FFFFFF!important}
section[data-testid="stSidebar"] .stSelectbox label{color:#94D2BD!important}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]>div{background:#162033!important;border-color:#0A9396!important;color:#fff!important}

/* ── Section label ── */
.section-label{font-size:13px;font-weight:600;color:#334155;margin-bottom:6px}

/* ── Footer ── */
.sac-footer{text-align:center;color:#94A3B8;font-size:11px;padding:14px 0;border-top:1px solid #1e293b;margin-top:16px}
.block-container{padding-top:0.8rem}
</style>
""", unsafe_allow_html=True)

# ── COLORS ────────────────────────────────────────────────────────────────────
TEAL, CORAL, GOLD, NAVY, GREEN, PURPLE = "#0A9396","#E76F51","#E9C46A","#0D1B2A","#1D9E75","#534AB7"
PALETTE = [TEAL, CORAL, GOLD, NAVY, GREEN, PURPLE, "#993C1D"]

BL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=11, color="#555"),
    margin=dict(l=8, r=8, t=36, b=8),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

# ── FULL BASE DATASET ─────────────────────────────────────────────────────────
# Shape: every cell = (zone, time_window, category)
# We store per-zone & per-time multipliers so filters produce realistic changes

ZONES      = ["Andheri","Bandra","Powai","Thane","Dadar"]
TIME_WINS  = ["6–9 AM","9 AM–12","12–3 PM","3–6 PM","6–10 PM","10 PM–2 AM"]
CATEGORIES = ["Snacks & Beverages","Fresh Produce","Dairy","Staples & Grains","Frozen Foods","Personal Care"]

# Base order volumes per (time × category)
BASE_VOL = {
    "Snacks & Beverages": [120,180,210,260,320,480],
    "Fresh Produce":      [280,310,220,190,140, 80],
    "Dairy":              [160,190,150,130,100, 50],
    "Staples & Grains":   [150,200,180,160,120, 60],
    "Frozen Foods":       [ 60, 80, 90,100, 95, 70],
    "Personal Care":      [ 40, 60, 70, 65, 55, 30],
}

# Zone multipliers (scale all volumes for that zone)
ZONE_MULT = {"All Zones":1.0,"Andheri":1.22,"Bandra":1.05,"Powai":0.88,"Thane":1.10,"Dadar":0.95}

# Time-window index lookup
TW_IDX = {tw:i for i,tw in enumerate(TIME_WINS)}

# Abandonment rates per category per zone
ABANDON_BASE = {
    "Fresh Produce":    {"All Zones":58,"Andheri":65,"Bandra":55,"Powai":48,"Thane":62,"Dadar":52},
    "Dairy":            {"All Zones":52,"Andheri":58,"Bandra":49,"Powai":42,"Thane":56,"Dadar":48},
    "Staples & Grains": {"All Zones":49,"Andheri":54,"Bandra":46,"Powai":40,"Thane":52,"Dadar":45},
    "Frozen Foods":     {"All Zones":38,"Andheri":42,"Bandra":36,"Powai":30,"Thane":40,"Dadar":35},
    "Snacks & Beverages":{"All Zones":24,"Andheri":27,"Bandra":22,"Powai":18,"Thane":26,"Dadar":21},
    "Personal Care":    {"All Zones":18,"Andheri":20,"Bandra":17,"Powai":14,"Thane":19,"Dadar":16},
}

# Waste risk per zone
WASTE_FRESH = {"All Zones":[82,65,48,71,55],"Andheri":[82,0,0,0,0],"Bandra":[0,65,0,0,0],
               "Powai":[0,0,48,0,0],"Thane":[0,0,0,71,0],"Dadar":[0,0,0,0,55]}
WASTE_DAIRY = {"All Zones":[68,52,38,62,45],"Andheri":[68,0,0,0,0],"Bandra":[0,52,0,0,0],
               "Powai":[0,0,38,0,0],"Thane":[0,0,0,62,0],"Dadar":[0,0,0,0,45]}

# Intent score by time window
INTENT_BASE  = [42,55,60,58,78,88]
INTENT_ZONE  = {"All Zones":0,"Andheri":8,"Bandra":3,"Powai":-5,"Thane":5,"Dadar":-2}

# ── HELPER: KPI card HTML ─────────────────────────────────────────────────────
def kpi(label, value, delta, delta_type="up", card_type=""):
    arrow = "↑" if delta_type=="up" else ("↓" if delta_type=="down" else "→")
    return f"""
    <div class="kpi-card {card_type}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <span class="kpi-delta {delta_type}">{arrow} {delta}</span>
    </div>"""

def kpi_row(*cards):
    inner = "".join(cards)
    st.markdown(f'<div class="kpi-grid">{inner}</div>', unsafe_allow_html=True)

# ── FILTER-AWARE DATA FUNCTIONS ────────────────────────────────────────────────
def get_timechart_data(zone_f, time_f, cat_f):
    zm = ZONE_MULT[zone_f]
    cats_to_show = CATEGORIES if cat_f == "All Categories" else [cat_f] if cat_f in BASE_VOL else CATEGORIES
    # Map UI category names to BASE_VOL keys
    cat_map = {"Snacks & Beverages":"Snacks & Beverages","Fresh Produce":"Fresh Produce",
               "Dairy":"Dairy","Staples & Grains":"Staples & Grains",
               "Frozen Foods":"Frozen Foods","Personal Care":"Personal Care"}
    result = {}
    for c in cats_to_show:
        key = cat_map.get(c, c)
        if key in BASE_VOL:
            vals = [round(v * zm) for v in BASE_VOL[key]]
            if time_f != "All Windows":
                idx = TW_IDX[time_f]
                vals = [vals[idx] if i==idx else 0 for i in range(len(TIME_WINS))]
            result[c] = vals
    return result

def get_abandon_data(zone_f, cat_f):
    cats = CATEGORIES if cat_f == "All Categories" else [cat_f] if cat_f in ABANDON_BASE else CATEGORIES
    labels, vals = [], []
    for c in cats:
        if c in ABANDON_BASE:
            labels.append(c)
            vals.append(ABANDON_BASE[c][zone_f])
    return labels, vals

def get_sessions_kpi(zone_f, time_f):
    base = 102400
    zm = ZONE_MULT[zone_f]
    tm = 1/6 if time_f != "All Windows" else 1.0
    return round(base * zm * tm)

def get_cart_kpi(zone_f):
    base = 312
    adjustments = {"All Zones":0,"Andheri":28,"Bandra":15,"Powai":-10,"Thane":8,"Dadar":-5}
    return base + adjustments[zone_f]

def get_abandon_kpi(zone_f, cat_f):
    if cat_f != "All Categories" and cat_f in ABANDON_BASE:
        return ABANDON_BASE[cat_f][zone_f]
    base = {"All Zones":63,"Andheri":70,"Bandra":60,"Powai":52,"Thane":67,"Dadar":58}
    return base[zone_f]

def get_waste_data(zone_f):
    if zone_f == "All Zones":
        return ZONES, WASTE_FRESH["All Zones"], WASTE_DAIRY["All Zones"]
    idx = ZONES.index(zone_f)
    return [zone_f], [WASTE_FRESH["All Zones"][idx]], [WASTE_DAIRY["All Zones"][idx]]

def get_intent(zone_f, time_f):
    adj = INTENT_ZONE[zone_f]
    scores = [min(100, max(0, v + adj)) for v in INTENT_BASE]
    if time_f != "All Windows":
        idx = TW_IDX[time_f]
        return [TIME_WINS[idx]], [scores[idx]]
    return TIME_WINS, scores

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 SAC Dashboard")
    st.markdown("**Team Real Madrid**")
    st.markdown("Q-Commerce Behavioral Analytics")
    st.divider()
    st.markdown("### 🎛️ Filters")
    zone_f = st.selectbox("📍 Location Zone", ["All Zones"]+ZONES)
    time_f = st.selectbox("⏰ Time Window",   ["All Windows"]+TIME_WINS)
    cat_f  = st.selectbox("📦 Product Category", ["All Categories"]+CATEGORIES)
    st.divider()
    st.markdown("### SAC Modules")
    st.markdown("✅ **SAC Modeler**")
    st.markdown("✅ **SAC Story**")
    st.markdown("✅ **Smart Predict**")
    st.markdown("✅ **SAC Planning**")
    st.divider()
    st.markdown(f"**Zone:** {zone_f}")
    st.markdown(f"**Time:** {time_f}")
    st.markdown(f"**Category:** {cat_f}")
    st.markdown("📊 2,00,000+ records")

# ── HEADER ────────────────────────────────────────────────────────────────────
active_filter = f"Zone: {zone_f}  ·  Time: {time_f}  ·  Category: {cat_f}"
st.markdown(f"""
<div class="sac-header">
  <div>
    <span class="sac-badge">SAC</span>&nbsp;&nbsp;
    <span class="sac-title">Q-Commerce Behavioral Analytics Dashboard</span>
    <p class="sac-subtitle">Powered by SAP Analytics Cloud · Team Real Madrid · Mumbai</p>
  </div>
  <div style="color:#94D2BD;font-size:11px;text-align:right">
    🎛️ Active filter: <strong style="color:#E9C46A">{active_filter}</strong><br>
    <span style="color:#5EEAD4">Charts update live with sidebar filters</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Behavioral Overview",
    "🛒  Cart Abandonment",
    "🧠  Smart Predict",
    "🏪  Dark Store Planning",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — BEHAVIORAL OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    sessions  = get_sessions_kpi(zone_f, time_f)
    cart_val  = get_cart_kpi(zone_f)
    ab_rate   = get_abandon_kpi(zone_f, cat_f)
    lift      = 150 + (ZONE_MULT[zone_f]-1)*80

    kpi_row(
        kpi("Total Sessions",       f"{sessions:,}",   "12% vs last week",        "up"),
        kpi("Avg Cart Value",        f"₹{cart_val}",   f"₹{round(lift)} cross-sell lift", "up",   "gold"),
        kpi("Abandonment Rate",      f"{ab_rate}%",    f"Target: <45%",           "down",  "warn"),
        kpi("Cross-sell Conversion", "40%",            "SAC Smart Predict",       "up",    "green"),
    )

    vol_data = get_timechart_data(zone_f, time_f, cat_f)
    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown('<p class="section-label">Order Volume by Time Window & Category · <em>SAC Story</em></p>', unsafe_allow_html=True)
        colors_map = {"Snacks & Beverages":TEAL,"Fresh Produce":CORAL,"Dairy":"#9B59B6",
                      "Staples & Grains":GOLD,"Frozen Foods":"#3498DB","Personal Care":GREEN}
        fig = go.Figure()
        for cat, vals in vol_data.items():
            fig.add_bar(name=cat, x=TIME_WINS, y=vals,
                        marker_color=colors_map.get(cat, NAVY), marker_cornerradius=3)
        fig.update_layout(barmode="stack", height=265, **BL,
                          xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if time_f == "10 PM–2 AM" or time_f == "All Windows":
            st.markdown('<span class="insight-teal">🌙 Late-night: +45% impulse spike in Snacks & Beverages</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-label">Session Duration Distribution · <em>SAC Story</em></p>', unsafe_allow_html=True)
        dur_mult = ZONE_MULT[zone_f]
        dur_vals = [round(v*dur_mult) for v in [18000,24000,22000,28000,10000]]
        fig2 = go.Figure(go.Bar(
            x=["0–60s","60–120s","120–180s","180–240s","240s+"],
            y=dur_vals, marker_cornerradius=3,
            marker_color=[TEAL, GREEN, GOLD, CORAL, "#993C1D"]
        ))
        fig2.update_layout(height=250, **BL, showlegend=False,
                           xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">⚠ Sessions >180s carry 70% abandonment risk</span>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-label">Category Share by Order Volume · <em>SAC Story</em></p>', unsafe_allow_html=True)
        if cat_f == "All Categories":
            pie_labels = ["Snacks & Bev","Fresh Produce","Staples","Personal Care","Frozen","Other"]
            pie_vals   = [28,22,19,12,11,8]
        else:
            pie_labels = [cat_f, "Others"]
            base_share = {"Snacks & Beverages":28,"Fresh Produce":22,"Dairy":14,
                          "Staples & Grains":19,"Frozen Foods":9,"Personal Care":8}
            s = base_share.get(cat_f, 15)
            pie_vals = [s, 100-s]
        fig3 = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals, hole=0.55,
            marker_colors=PALETTE, textinfo="label+percent", textfont_size=10
        ))
        fig3.update_layout(height=235, **BL, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col4:
        st.markdown('<p class="section-label">Cross-sell Conversion by Bundle · <em>SAC KPI</em></p>', unsafe_allow_html=True)
        zm = ZONE_MULT[zone_f]
        cross_vals = [round(v*zm) for v in [40,33,27,21,16]]
        fig4 = go.Figure(go.Bar(
            y=["Snacks + Bev","Dairy + Breakfast","Frozen + Snacks","Grains + Staples","Personal + Bev"],
            x=cross_vals, orientation="h",
            marker_color=[TEAL,GREEN,GOLD,CORAL,"#993C1D"], marker_cornerradius=3,
            text=[f"{v}%" for v in cross_vals], textposition="outside"
        ))
        fig4.update_layout(height=235, **BL, showlegend=False,
                           xaxis=dict(range=[0,60], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — CART ABANDONMENT
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    ab_labels, ab_vals = get_abandon_data(zone_f, cat_f)
    top_ab   = max(ab_vals) if ab_vals else 58
    top_cat  = ab_labels[ab_vals.index(top_ab)] if ab_vals else "Fresh Produce"
    recovery = round(38 * ZONE_MULT[zone_f])

    kpi_row(
        kpi("Highest Abandon Category", top_cat,          f"{top_ab}% drop-off",        "down", "warn"),
        kpi("Avg Drop-off Session",     "194s",            "Choice overload threshold",   "down", "warn"),
        kpi("Recovery Opportunity",     f"₹{recovery}L/mo",f"If abandonment → 45%",      "up",   "gold"),
        kpi("Top Trigger",              "Choice Overload", "Staples category",            "neutral"),
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-label">Conversion Funnel — All Sessions · <em>SAC Story</em></p>', unsafe_allow_html=True)
        zm = ZONE_MULT[zone_f]
        funnel_x = [round(v*zm) for v in [100000,72000,41000,22000,14000]]
        fig5 = go.Figure(go.Funnel(
            y=["App Sessions","Product Views","Add to Cart","Checkout Start","Order Complete"],
            x=funnel_x, textinfo="value+percent initial",
            marker=dict(color=[NAVY,TEAL,GREEN,GOLD,CORAL]),
            connector=dict(line=dict(color="#ccc", width=1))
        ))
        fig5.update_layout(height=295, **BL)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">⚠ 86% of sessions do not result in a completed order</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-label">Abandonment Rate by Category · <em>SAC Dashboard</em></p>', unsafe_allow_html=True)
        ab_colors = [CORAL if v>50 else GOLD if v>35 else TEAL for v in ab_vals]
        fig6 = go.Figure(go.Bar(
            y=ab_labels, x=ab_vals, orientation="h",
            marker_color=ab_colors, marker_cornerradius=3,
            text=[f"{v}%" for v in ab_vals], textposition="outside"
        ))
        fig6.update_layout(height=295, **BL, showlegend=False,
                           xaxis=dict(range=[0,80], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False))
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-gold">Fresh Produce & Dairy are highest-priority intervention categories</span>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Abandonment Rate by Time Window & Zone · <em>SAC Story</em></p>', unsafe_allow_html=True)
    zones_show = [zone_f] if zone_f != "All Zones" else ZONES
    ab_heat = {
        "All Zones": [[55,48,41,52,44],[58,51,44,55,47],[61,54,47,58,50],[64,57,50,61,53],[74,67,57,68,60],[69,62,52,65,57]],
        "Andheri":   [[62,0,0,0,0],[65,0,0,0,0],[68,0,0,0,0],[71,0,0,0,0],[82,0,0,0,0],[76,0,0,0,0]],
        "Bandra":    [[0,48,0,0,0],[0,51,0,0,0],[0,54,0,0,0],[0,57,0,0,0],[0,67,0,0,0],[0,62,0,0,0]],
        "Powai":     [[0,0,41,0,0],[0,0,44,0,0],[0,0,47,0,0],[0,0,50,0,0],[0,0,57,0,0],[0,0,52,0,0]],
        "Thane":     [[0,0,0,52,0],[0,0,0,55,0],[0,0,0,58,0],[0,0,0,61,0],[0,0,0,68,0],[0,0,0,65,0]],
        "Dadar":     [[0,0,0,0,44],[0,0,0,0,47],[0,0,0,0,50],[0,0,0,0,53],[0,0,0,0,60],[0,0,0,0,57]],
    }
    bar_cols = [NAVY, TEAL, GREEN, GOLD, CORAL, "#993C1D"]
    time_show = [time_f] if time_f != "All Windows" else TIME_WINS
    fig7 = go.Figure()
    for tw in time_show:
        ti = TW_IDX[tw]
        row = ab_heat[zone_f][ti]
        y_vals = [row[ZONES.index(z)] for z in zones_show] if zone_f=="All Zones" else [ab_heat[zone_f][ti][ZONES.index(zone_f)]]
        fig7.add_bar(name=tw, x=zones_show, y=y_vals,
                     marker_color=bar_cols[ti], marker_cornerradius=2)
    fig7.update_layout(barmode="group", height=230, **BL,
                       yaxis=dict(ticksuffix="%", gridcolor="#f0f0f0"),
                       xaxis=dict(showgrid=False))
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — SMART PREDICT
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    zm = ZONE_MULT[zone_f]
    top_pred  = round(72 * min(zm, 1.3))
    churn_cnt = round(8240 * zm)

    kpi_row(
        kpi("Model Accuracy",     "84%",            "Smart Predict classification","up"),
        kpi("Top Cross-sell",     "Snacks",         f"{top_pred}% predicted conv", "up",   "gold"),
        kpi("Churn-Risk Users",   f"{churn_cnt:,}", "Low freq + high recency gap", "down", "warn"),
        kpi("Best Intervention",  "10 PM–2 AM",     "Highest uplift window",       "up",   "green"),
    )

    col1, col2 = st.columns([1.1, 1])
    with col1:
        st.markdown('<p class="section-label">Predicted Cross-sell Conversion Probability · <em>Smart Predict</em></p>', unsafe_allow_html=True)
        base_preds = [72,68,58,44,31,22]
        pred_vals  = [min(99, round(v*zm)) for v in base_preds]
        p_colors   = [TEAL if v>=60 else GOLD if v>=40 else CORAL for v in pred_vals]
        fig8 = go.Figure(go.Bar(
            y=["Snacks","Chocolates","Beverages","Dairy","Frozen Foods","Grains"],
            x=pred_vals, orientation="h",
            marker_color=p_colors, marker_cornerradius=4,
            text=[f"{v}%" for v in pred_vals], textposition="outside",
            textfont=dict(size=12, color="#333")
        ))
        fig8.add_vline(x=50, line_dash="dash", line_color=CORAL,
                       annotation_text="50% threshold", annotation_font_size=10)
        fig8.update_layout(height=285, **BL, showlegend=False,
                           xaxis=dict(range=[0,110], ticksuffix="%", showgrid=False),
                           yaxis=dict(showgrid=False, tickfont=dict(size=12)))
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-teal">Push Snacks + Chocolates after 10 PM for maximum ROI</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-label">Churn Risk Segmentation · <em>Smart Predict</em></p>', unsafe_allow_html=True)
        fig9 = go.Figure(go.Pie(
            labels=["Low risk","Medium risk","High risk","At-risk returning"],
            values=[12,28,38,22], hole=0.5,
            marker_colors=[TEAL,GOLD,CORAL,PURPLE],
            textinfo="label+percent", textfont_size=11,
            pull=[0,0,0.08,0]
        ))
        fig9.update_layout(height=280, **BL)
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">38% high-risk segment needs immediate targeted offer</span>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Purchase Intent Score by Time Window · <em>Smart Predict · Behavioral Trigger Index</em></p>', unsafe_allow_html=True)
    x_intent, y_intent = get_intent(zone_f, time_f)
    fig10 = go.Figure()
    fig10.add_scatter(x=x_intent, y=y_intent, mode="lines+markers",
                      line=dict(color=TEAL, width=3),
                      fill="tozeroy", fillcolor="rgba(10,147,150,0.12)",
                      marker=dict(color=TEAL, size=9))
    fig10.add_hrect(y0=75, y1=100, fillcolor="rgba(10,147,150,0.08)", line_width=0,
                    annotation_text="High intent zone", annotation_position="right",
                    annotation_font_size=10)
    fig10.update_layout(height=205, **BL, showlegend=False,
                        yaxis=dict(range=[0,105], ticksuffix="%", gridcolor="#f0f0f0"),
                        xaxis=dict(showgrid=False))
    st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})
    st.markdown('<span class="insight-gold">Late-night window has highest intent — prime for predictive push notifications</span>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — DARK STORE PLANNING
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    w_zones, w_fresh, w_dairy = get_waste_data(zone_f)
    high_risk = sum(1 for v in w_fresh if v>60)
    overstock = round(12.4 * ZONE_MULT[zone_f], 1)

    kpi_row(
        kpi("High Waste Risk Zones",    f"{high_risk} / {len(w_zones)}", "Zones above action threshold", "down","warn"),
        kpi("Projected Waste Saving",   "30%",            "With SAC Planning integrated",  "up",   "green"),
        kpi("Fresh Produce Overstock",  f"₹{overstock}L/wk","Weekly exposure",            "down", "warn"),
        kpi("Planning Version",         "v3 — Active",    "SAC Planning live",             "up",   "gold"),
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-label">Perishable Waste Risk by Zone & Category · <em>SAC Planning</em></p>', unsafe_allow_html=True)
        fig11 = go.Figure()
        fig11.add_bar(name="Fresh Produce", y=w_zones, x=w_fresh,
                      orientation="h", marker_color=CORAL, marker_cornerradius=3)
        fig11.add_bar(name="Dairy", y=w_zones, x=w_dairy,
                      orientation="h", marker_color=GOLD, marker_cornerradius=3)
        fig11.add_vline(x=60, line_dash="dash", line_color="#aaa",
                        annotation_text="Action threshold (60)", annotation_font_size=10)
        fig11.update_layout(barmode="group", height=290, **BL,
                            xaxis=dict(range=[0,100], showgrid=False),
                            yaxis=dict(showgrid=False))
        st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">Andheri & Thane exceed action threshold — procurement adjustment required</span>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-label">Dark Store Inventory vs SAC Demand Forecast · <em>SAC Planning</em></p>', unsafe_allow_html=True)
        base_demand = {"All Zones":[60,88,93,72,80],"Andheri":[60],"Bandra":[88],"Powai":[93],"Thane":[72],"Dadar":[80]}
        inv_zones_show = [zone_f] if zone_f != "All Zones" else ZONES
        inv_demand = base_demand[zone_f]
        inv_stock  = [100]*len(inv_zones_show)
        fig12 = go.Figure()
        fig12.add_bar(name="Current Stock (index)", x=inv_zones_show, y=inv_stock,
                      marker_color=NAVY, marker_cornerradius=3, opacity=0.7)
        fig12.add_bar(name="SAC Demand Forecast", x=inv_zones_show, y=inv_demand,
                      marker_color=TEAL, marker_cornerradius=3)
        fig12.update_layout(barmode="group", height=275, **BL,
                            yaxis=dict(ticksuffix=" idx", gridcolor="#f0f0f0"),
                            xaxis=dict(showgrid=False))
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})
        st.markdown('<span class="insight-red">Andheri: 40% overstock vs forecasted behavioral demand</span>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Procurement Adjustment Recommendations · <em>SAC Planning · Action Trigger</em></p>', unsafe_allow_html=True)
    all_recs = {
        "Andheri": ("🔴 High (82)",  "Reduce Fresh Produce −35%", "94%", "₹3.2L",  "URGENT"),
        "Bandra":  ("🟡 Medium (65)","Increase Snacks +12%",      "87%", "—",       "MODERATE"),
        "Powai":   ("🟢 Low (48)",   "Maintain current levels",   "91%", "—",       "STABLE"),
        "Thane":   ("🔴 High (71)",  "Reduce Dairy −28%",         "89%", "₹2.8L",  "URGENT"),
        "Dadar":   ("🟡 Medium (55)","Reduce Fresh Produce −20%", "85%", "₹1.6L",  "MODERATE"),
    }
    zones_for_table = [zone_f] if zone_f != "All Zones" else ZONES
    recs_df = pd.DataFrame([
        {"Zone":z,"Waste Risk":all_recs[z][0],"Recommended Action":all_recs[z][1],
         "SAC Confidence":all_recs[z][2],"Est. Weekly Saving":all_recs[z][3],"Priority":all_recs[z][4]}
        for z in zones_for_table
    ])
    def style_priority(val):
        if val=="URGENT":   return "background-color:#3D1515;color:#FCA5A5;font-weight:700"
        if val=="MODERATE": return "background-color:#3D2E0A;color:#FCD34D;font-weight:700"
        return "background-color:#0F3D3E;color:#5EEAD4;font-weight:700"
    st.dataframe(recs_df.style.applymap(style_priority, subset=["Priority"]),
                 use_container_width=True, hide_index=True, height=210)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sac-footer">
SAP Analytics Cloud &nbsp;·&nbsp; Q-Commerce Behavioral Dataset &nbsp;·&nbsp;
2,00,000+ records &nbsp;·&nbsp; Mumbai Zones &nbsp;·&nbsp;
<strong>Team Real Madrid</strong> &nbsp;·&nbsp; University Presentation 2025
</div>
""", unsafe_allow_html=True)
