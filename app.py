import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="SAC Q-Commerce Dashboard · Team Real Madrid",
    page_icon="🛒", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}
.kpi-card{background:#162033;border-radius:12px;padding:18px 20px;border-left:5px solid #0A9396}
.kpi-card.warn{border-left-color:#FF6B6B}.kpi-card.gold{border-left-color:#FFD166}.kpi-card.green{border-left-color:#06D6A0}
.kpi-label{font-size:11px;font-weight:700;color:#7ECECA;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.kpi-value{font-size:34px;font-weight:800;color:#FFFFFF;line-height:1.1;margin-bottom:8px}
.kpi-delta{font-size:12px;font-weight:600;padding:4px 10px;border-radius:10px;display:inline-block}
.kpi-delta.up{background:rgba(6,214,160,0.2);color:#06D6A0}
.kpi-delta.down{background:rgba(255,107,107,0.2);color:#FF6B6B}
.kpi-delta.neutral{background:rgba(126,206,206,0.15);color:#7ECECA}
.insight-teal{display:inline-block;background:#0A2A2B;color:#2FFFD1;font-size:12px;font-weight:600;padding:6px 14px;border-radius:20px;margin-top:8px;border:1px solid #0A9396}
.insight-red{display:inline-block;background:#2B0A0A;color:#FF9999;font-size:12px;font-weight:600;padding:6px 14px;border-radius:20px;margin-top:8px;border:1px solid #FF6B6B}
.insight-gold{display:inline-block;background:#2B1F00;color:#FFE066;font-size:12px;font-weight:600;padding:6px 14px;border-radius:20px;margin-top:8px;border:1px solid #FFD166}
.sac-header{background:#0D1B2A;padding:14px 22px;border-radius:10px;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between;border:1px solid #1E3A5F}
.sac-badge{background:#0A9396;color:#fff;font-size:11px;font-weight:800;padding:4px 10px;border-radius:5px;letter-spacing:1.5px}
.sac-title{color:#fff;font-size:17px;font-weight:700;margin:0}
.sac-subtitle{color:#7ECECA;font-size:11px;margin:3px 0 0 0}
.filter-pill{color:#FFD166;font-weight:600;font-size:11px}
.slbl{font-size:13px;font-weight:700;color:#7ECECA;margin-bottom:6px;letter-spacing:.3px}
.sac-footer{text-align:center;color:#4A6FA5;font-size:11px;padding:14px 0;border-top:1px solid #1E3A5F;margin-top:16px}
.block-container{padding-top:0.8rem}
/* ── Inline filter bar ── */
.filter-bar{background:#0D1B2A;border:1px solid #1E3A5F;border-radius:10px;padding:12px 18px;margin-bottom:14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.filter-tag{color:#7ECECA;font-size:11px;font-weight:700;letter-spacing:.5px;white-space:nowrap}
.sac-modules{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.mod-badge{background:#162033;border:1px solid #1E3A5F;border-radius:6px;padding:4px 10px;font-size:11px;color:#7ECECA;font-weight:600}
#MainMenu{visibility:hidden!important;display:none!important}
header[data-testid="stHeader"]{visibility:hidden!important;display:none!important}
footer{visibility:hidden!important;display:none!important}
div[data-testid="stToolbar"]{visibility:hidden!important;display:none!important}
div[data-testid="stDecoration"]{visibility:hidden!important;display:none!important}
div[data-testid="stStatusWidget"]{visibility:hidden!important;display:none!important}
.stDeployButton{visibility:hidden!important;display:none!important}
.viewerBadge_container__1QSob{display:none!important}


</style>
""", unsafe_allow_html=True)

# ── COLORS ────────────────────────────────────────────────────────────────────
CT = "#2FFFD1"; CR = "#FF6B6B"; CG = "#FFD166"
CB = "#4FC3F7"; CGR = "#69F0AE"; CP = "#CE93D8"
CO = "#FFAB40"; CN = "#4A6FA5"
CPAL = [CT, CR, CG, CB, CGR, CP, CO]

# Base layout — NO font key here, set per-chart to avoid duplicate key crash
BL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,27,42,0.7)",
    margin=dict(l=8, r=8, t=40, b=8),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="left", x=0,
        font=dict(color="#D0E4F0", size=11),
        bgcolor="rgba(0,0,0,0)"
    ),
)

def mk_layout(**extra):
    """Merge BL + font + any extra kwargs safely (no duplicate keys)."""
    return {**BL, "font": dict(family="sans-serif", size=11, color="#B0C4D8"), **extra}

def ax(suffix="", grid=False):
    return dict(
        showgrid=grid, gridcolor="#1E3A5F", tickcolor="#4A6FA5",
        linecolor="#1E3A5F", tickfont=dict(color="#B0C4D8"),
        ticksuffix=suffix
    )

# ── LOOKUP DATA ───────────────────────────────────────────────────────────────
ZONES      = ["Andheri","Bandra","Powai","Thane","Dadar"]
TIME_WINS  = ["6–9 AM","9 AM–12","12–3 PM","3–6 PM","6–10 PM","10 PM–2 AM"]
CATEGORIES = ["Snacks & Beverages","Fresh Produce","Dairy",
              "Staples & Grains","Frozen Foods","Personal Care"]
TW_IDX     = {tw: i for i, tw in enumerate(TIME_WINS)}

BASE_VOL = {
    "Snacks & Beverages": [120,180,210,260,320,480],
    "Fresh Produce":      [280,310,220,190,140, 80],
    "Dairy":              [160,190,150,130,100, 50],
    "Staples & Grains":   [150,200,180,160,120, 60],
    "Frozen Foods":       [ 60, 80, 90,100, 95, 70],
    "Personal Care":      [ 40, 60, 70, 65, 55, 30],
}

ZONE_MULT = {"All Zones":1.0,"Andheri":1.22,"Bandra":1.05,"Powai":0.88,"Thane":1.10,"Dadar":0.95}

# Sessions per time window (daily total split across windows realistically)
# All Windows = full day = 102,400 baseline. Single window = that window's share.
TW_SHARE = {"All Windows":1.0,"6–9 AM":0.10,"9 AM–12":0.15,"12–3 PM":0.14,
            "3–6 PM":0.15,"6–10 PM":0.25,"10 PM–2 AM":0.21}

# Abandonment rates per (category, zone)
ABANDON = {
    "Fresh Produce":     {"All Zones":58,"Andheri":65,"Bandra":55,"Powai":48,"Thane":62,"Dadar":52},
    "Dairy":             {"All Zones":52,"Andheri":58,"Bandra":49,"Powai":42,"Thane":56,"Dadar":48},
    "Staples & Grains":  {"All Zones":49,"Andheri":54,"Bandra":46,"Powai":40,"Thane":52,"Dadar":45},
    "Frozen Foods":      {"All Zones":38,"Andheri":42,"Bandra":36,"Powai":30,"Thane":40,"Dadar":35},
    "Snacks & Beverages":{"All Zones":24,"Andheri":27,"Bandra":22,"Powai":18,"Thane":26,"Dadar":21},
    "Personal Care":     {"All Zones":18,"Andheri":20,"Bandra":17,"Powai":14,"Thane":19,"Dadar":16},
}

# Time-window abandonment adjustment (evening/late-night harder to convert)
TW_AB = {"All Windows":0,"6–9 AM":-8,"9 AM–12":-4,"12–3 PM":0,"3–6 PM":2,"6–10 PM":10,"10 PM–2 AM":14}

CART_BASE = {"All Zones":312,"Andheri":340,"Bandra":328,"Powai":295,"Thane":318,"Dadar":302}
CART_TW   = {"All Windows":0,"6–9 AM":-22,"9 AM–12":-10,"12–3 PM":0,"3–6 PM":8,"6–10 PM":28,"10 PM–2 AM":42}

INTENT    = [42,55,60,58,78,88]
INTENT_Z  = {"All Zones":0,"Andheri":8,"Bandra":3,"Powai":-5,"Thane":5,"Dadar":-2}

WASTE_F   = {"All Zones":[82,65,48,71,55],"Andheri":[82],"Bandra":[65],"Powai":[48],"Thane":[71],"Dadar":[55]}
WASTE_D   = {"All Zones":[68,52,38,62,45],"Andheri":[68],"Bandra":[52],"Powai":[38],"Thane":[62],"Dadar":[45]}

CAT_WF    = {"All Categories":1.0,"Fresh Produce":1.35,"Dairy":1.20,
             "Staples & Grains":0.85,"Snacks & Beverages":0.70,
             "Frozen Foods":0.90,"Personal Care":0.50}

RECS_BASE = {
    "Andheri": ("Reduce Fresh Produce −35%", "94%", "₹3.2L"),
    "Bandra":  ("Increase Snacks +12%",      "87%", "—"),
    "Powai":   ("Maintain current levels",   "91%", "—"),
    "Thane":   ("Reduce Dairy −28%",         "89%", "₹2.8L"),
    "Dadar":   ("Reduce Fresh Produce −20%", "85%", "₹1.6L"),
}

DEMAND_BASE = {"All Zones":[60,88,93,72,80],"Andheri":[60],"Bandra":[88],"Powai":[93],"Thane":[72],"Dadar":[80]}

# ── COMPUTE FUNCTIONS ─────────────────────────────────────────────────────────
def c_sessions(z, t):
    """Total sessions = daily baseline × zone_mult × time_window_share."""
    return round(102400 * ZONE_MULT[z] * TW_SHARE[t])

def c_cart(z, t):
    return CART_BASE[z] + CART_TW[t]

def c_abandon(z, t, cat):
    if cat != "All Categories":
        base = ABANDON.get(cat, {}).get(z, 45)
    else:
        base = round(sum(ABANDON[c][z] for c in CATEGORIES) / len(CATEGORIES))
    return min(95, base + TW_AB[t])

def c_cross(z, t):
    tm = min(TW_SHARE[t] / TW_SHARE["All Windows"] * 6, 1.3)  # relative to avg window
    return min(99, round(40 * ZONE_MULT[z] * tm))

def c_preds(z, t):
    cats = ["Snacks","Chocolates","Beverages","Dairy","Frozen","Grains"]
    base = [72, 68, 58, 44, 31, 22]
    zm = ZONE_MULT[z]
    # Late-night boosts snack/choc, morning boosts dairy
    tw_boost = {"All Windows":1.0,"6–9 AM":0.85,"9 AM–12":0.92,"12–3 PM":0.95,
                "3–6 PM":1.0,"6–10 PM":1.12,"10 PM–2 AM":1.20}
    dairy_boost = {"All Windows":1.0,"6–9 AM":1.25,"9 AM–12":1.15,"12–3 PM":1.0,
                   "3–6 PM":0.95,"6–10 PM":0.85,"10 PM–2 AM":0.80}
    boosts = [tw_boost[t], tw_boost[t], tw_boost[t], dairy_boost[t], tw_boost[t], tw_boost[t]]
    vals = [min(99, round(base[i] * zm * boosts[i])) for i in range(len(cats))]
    bi = vals.index(max(vals))
    return cats, vals, cats[bi], vals[bi]

def c_churn(z, t, cat):
    zm = ZONE_MULT[z]
    tm = 0.5 if t in ["6–9 AM","9 AM–12"] else 1.25 if t in ["6–10 PM","10 PM–2 AM"] else 1.0
    cm = 1.3 if cat in ["Fresh Produce","Dairy"] else 0.75 if cat == "Snacks & Beverages" else 1.0
    return round(8240 * zm * tm * cm)

def c_intent(z, t):
    adj = INTENT_Z[z]
    scores = [min(100, max(0, v + adj)) for v in INTENT]
    if t == "All Windows":
        return TIME_WINS[:], scores[:]
    return [t], [scores[TW_IDX[t]]]

def c_best_tw(z, t):
    adj = INTENT_Z[z]
    scores = [min(100, v + adj) for v in INTENT]
    if t != "All Windows":
        return t, scores[TW_IDX[t]]
    bi = scores.index(max(scores))
    return TIME_WINS[bi], scores[bi]

def c_waste(z, cat):
    cf = CAT_WF[cat]
    zones = ZONES if z == "All Zones" else [z]
    fresh = [round(v * cf) for v in WASTE_F[z]]
    dairy = [round(v * cf) for v in WASTE_D[z]]
    return zones, fresh, dairy

def c_overstock(z, cat, t):
    tm = 1.3 if t in ["6–10 PM","10 PM–2 AM"] else 0.8 if t in ["6–9 AM","9 AM–12"] else 1.0
    return round(12.4 * ZONE_MULT[z] * CAT_WF[cat] * tm, 1)

def c_waste_sav(z, cat):
    base = 38 if z in ["Andheri","Thane"] else 28 if z in ["Bandra","Dadar"] else 30
    if cat in ["Fresh Produce","Dairy"]:
        base = min(48, base + 8)
    return base

def c_vol(z, t, cat):
    zm = ZONE_MULT[z]
    cats = [cat] if cat != "All Categories" else list(BASE_VOL.keys())
    out = {}
    for c in cats:
        if c not in BASE_VOL:
            continue
        vals = [round(v * zm) for v in BASE_VOL[c]]
        if t != "All Windows":
            idx = TW_IDX[t]
            vals = [vals[idx] if i == idx else 0 for i in range(len(TIME_WINS))]
        out[c] = vals
    return out

def c_ab_chart(z, t, cat):
    cats = [cat] if cat != "All Categories" else CATEGORIES
    labs, vals = [], []
    for c in cats:
        base = ABANDON.get(c, {}).get(z, 30)
        labs.append(c)
        vals.append(min(95, base + TW_AB[t]))
    return labs, vals

def c_funnel(z, t):
    base = [100000, 72000, 41000, 22000, 14000]
    tm = TW_SHARE[t]
    zm = ZONE_MULT[z]
    return [round(v * zm * tm) for v in base]

def c_churn_pie(z, cat):
    if z in ["Andheri","Thane"] or cat in ["Fresh Produce","Dairy"]:
        return [8, 22, 46, 24]
    elif z == "Powai":
        return [20, 34, 28, 18]
    elif cat == "Snacks & Beverages":
        return [22, 36, 26, 16]
    return [12, 28, 38, 22]

def c_recs(z, cat):
    zones = ZONES if z == "All Zones" else [z]
    rows = []
    for zn in zones:
        action, conf, saving = RECS_BASE[zn]
        if cat == "Dairy" and "Fresh Produce" in action:
            action = action.replace("Fresh Produce", "Dairy")
        elif cat == "Snacks & Beverages" and "Reduce" in action and zn not in ["Andheri","Thane"]:
            action = "Increase Snacks & Beverages +15%"
        # Get correct waste score for this zone
        zi = ZONES.index(zn)
        raw = WASTE_F["All Zones"][zi]
        adj = round(raw * CAT_WF[cat])
        if adj > 68:   risk, pri = f"🔴 High ({adj})",   "URGENT"
        elif adj > 52: risk, pri = f"🟡 Medium ({adj})", "MODERATE"
        else:          risk, pri = f"🟢 Low ({adj})",    "STABLE"
        rows.append({"Zone":zn,"Waste Risk":risk,"Recommended Action":action,
                     "SAC Confidence":conf,"Est. Weekly Saving":saving,"Priority":pri})
    return pd.DataFrame(rows)

def c_inv_demand(z, cat):
    vals = DEMAND_BASE[z]
    return [round(v * CAT_WF[cat]) for v in vals]

# ── INSIGHT GENERATORS ────────────────────────────────────────────────────────
def ins_vol(z, t, cat):
    if t == "10 PM–2 AM":
        c = cat if cat != "All Categories" else "Snacks & Beverages"
        return "teal", f"🌙 Late-night surge in {c} · {z} — impulse buying peaks after 10 PM"
    if t == "6–9 AM":
        return "teal", f"🌅 Morning slot · {z}: Fresh Produce & Dairy dominate — routine purchase window"
    if t == "6–10 PM":
        return "gold", f"⚡ Evening peak · {z}: highest combined volume — prime cross-sell window"
    if cat == "Fresh Produce":
        return "red",  f"⚠ Fresh Produce drops sharply after 6 PM in {z} — late orders create waste risk"
    if cat == "Snacks & Beverages":
        return "teal", f"🍿 Snacks & Beverages grow steadily through the day in {z}, peaking late-night"
    if z == "Andheri":
        return "gold", "📍 Andheri volumes are 22% above city average across all categories"
    if z == "Powai":
        return "teal", "📍 Powai has lower volumes but highest cross-sell conversion sensitivity"
    return "teal", "🌙 Late-night (10 PM–2 AM) drives +45% impulse buying — activate recommendation widgets"

def ins_funnel(z, t, pct):
    if pct < 11:
        return "red",  f"⚠ Only {pct}% completion in {z} · {t} — critical UX intervention needed"
    if t in ["6–10 PM","10 PM–2 AM"]:
        return "gold", f"⚡ {t} · {z}: highest abandonment pressure — simplify checkout flow now"
    if z == "Andheri":
        return "red",  f"⚠ Andheri: {100-pct}% sessions lost — SKU overload causing choice paralysis"
    return "red",  f"⚠ {100-pct}% of sessions do not complete an order in {z} — funnel needs optimisation"

def ins_abandon(z, t, cat, top_cat, top_val):
    if t in ["6–10 PM","10 PM–2 AM"]:
        return "red",  f"⚠ {t}: abandonment +{TW_AB[t]}% above baseline in {z} — decision fatigue at peak load"
    if top_val > 60:
        return "red",  f"⚠ {top_cat} at {top_val}% in {z} — reduce displayed SKUs to cut choice overload"
    if top_val < 25:
        return "teal", f"✅ {top_cat} has low {top_val}% abandonment in {z} — ideal for cross-sell push"
    if z == "Powai":
        return "teal", "✅ Powai shows lowest abandonment city-wide — best zone for new category pilots"
    return "gold", f"📊 {top_cat} highest drop-off at {top_val}% in {z} · {t} — UX simplification needed"

def ins_predict(z, t, top_cat, top_pct):
    if t == "10 PM–2 AM":
        return "teal", f"🎯 {z} · {t}: {top_cat} at {top_pct}% — trigger late-night recommendation widget now"
    if t == "6–9 AM":
        return "gold", f"🌅 Morning · {z}: Dairy + Breakfast bundle shows best conversion — push at 7 AM"
    if top_pct >= 75:
        return "teal", f"🚀 {top_cat} at {top_pct}% exceeds 70% threshold in {z} — fire push notification"
    if z == "Powai":
        return "teal", f"📍 Powai: {top_cat} bundles show strong response despite lower basket size"
    return "gold", f"💡 Push {top_cat} bundles in {z} · {t} — predicted {top_pct}% conversion"

def ins_darkstore(z, cat, t, saving):
    if t in ["6–10 PM","10 PM–2 AM"] and cat in ["Fresh Produce","All Categories"]:
        return "red",  f"⚠ Evening/late abandonment spiking in {z} — cut Fresh Produce procurement −30% next cycle"
    if cat == "Dairy":
        return "red",  f"⚠ Dairy abandonment feeding overstock in {z} — reduce Dairy procurement this week"
    if saving >= 38:
        return "teal", f"✅ SAC Planning recovers {saving}% waste cost in {z} — priority procurement zone"
    if z == "Powai":
        return "teal", "✅ Powai waste risk LOW — maintain levels, redirect budget to cross-sell campaigns"
    if z == "All Zones":
        return "gold", f"📦 SAC Planning reduces city-wide perishable waste by {saving}% this week"
    return "gold", f"📦 SAC Planning reduces {z} · {cat} waste by {saving}% this procurement cycle"

# ── UI HELPERS ────────────────────────────────────────────────────────────────
def kpi(label, value, delta, dt="up", ct=""):
    a = "↑" if dt=="up" else "↓" if dt=="down" else "→"
    return (f'<div class="kpi-card {ct}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<span class="kpi-delta {dt}">{a} {delta}</span></div>')

def kpi_row(*cards):
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

def badge(t, msg):
    st.markdown(f'<span class="insight-{t}">{msg}</span>', unsafe_allow_html=True)

def slbl(txt):
    st.markdown(f'<p class="slbl">{txt}</p>', unsafe_allow_html=True)

CAT_COL = {
    "Snacks & Beverages": CT, "Fresh Produce": CR, "Dairy": CB,
    "Staples & Grains": CG, "Frozen Foods": CP, "Personal Care": CGR,
}

# ── INLINE FILTER BAR (no sidebar — works on all Streamlit versions) ─────────
# SAC Module badges
st.markdown(
    '<div class="sac-modules">'
    '<span class="mod-badge">✅ SAC Modeler</span>'
    '<span class="mod-badge">✅ SAC Story</span>'
    '<span class="mod-badge">✅ Smart Predict</span>'
    '<span class="mod-badge">✅ SAC Planning</span>'
    '<span style="margin-left:auto;color:#4A6FA5;font-size:10px;align-self:center">Dataset: 2,00,000+ records · Mumbai</span>'
    '</div>',
    unsafe_allow_html=True
)

# Filters as 3 columns inline
fc1, fc2, fc3 = st.columns(3)
with fc1:
    zone_f = st.selectbox("📍 Location Zone",    ["All Zones"] + ZONES)
with fc2:
    time_f = st.selectbox("⏰ Time Window",       ["All Windows"] + TIME_WINS)
with fc3:
    cat_f  = st.selectbox("📦 Product Category", ["All Categories"] + CATEGORIES)

# ── PRE-COMPUTE ALL FILTER-DEPENDENT VALUES ───────────────────────────────────
sessions   = c_sessions(zone_f, time_f)
cart_val   = c_cart(zone_f, time_f)
ab_rate    = c_abandon(zone_f, time_f, cat_f)
cross_pct  = c_cross(zone_f, time_f)
p_cats, pred_vals, top_cat, top_pct = c_preds(zone_f, time_f)
churn_cnt  = c_churn(zone_f, time_f, cat_f)
x_int, y_int = c_intent(zone_f, time_f)
best_tw, best_score = c_best_tw(zone_f, time_f)
w_zones, w_fresh, w_dairy = c_waste(zone_f, cat_f)
overstock  = c_overstock(zone_f, cat_f, time_f)
waste_sav  = c_waste_sav(zone_f, cat_f)
high_risk  = sum(1 for v in w_fresh if v > 60)
ab_labs, ab_vals = c_ab_chart(zone_f, time_f, cat_f)
top_ab_cat = ab_labs[ab_vals.index(max(ab_vals))] if ab_vals else "Fresh Produce"
top_ab_val = max(ab_vals) if ab_vals else 58
vol_data   = c_vol(zone_f, time_f, cat_f)
funnel_v   = c_funnel(zone_f, time_f)
churn_pie  = c_churn_pie(zone_f, cat_f)
recs_df    = c_recs(zone_f, cat_f)
cross_ch   = [min(99, round(v * ZONE_MULT[zone_f])) for v in [40,33,27,21,16]]
completion = round(funnel_v[-1] / funnel_v[0] * 100) if funnel_v[0] > 0 else 14
model_acc  = round(84 + INTENT_Z[zone_f] * 0.3)
inv_demand = c_inv_demand(zone_f, cat_f)
inv_stock  = [100] * len(w_zones)
max_gap_z  = w_zones[inv_demand.index(min(inv_demand))]
max_gap    = 100 - min(inv_demand)
avg_sess   = round(194 + TW_AB[time_f] * 3)
recovery   = round(38 * ZONE_MULT[zone_f] * (1.2 if ab_rate > 55 else 1.0))

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sac-header">
  <div>
    <span class="sac-badge">SAC</span>&nbsp;&nbsp;
    <span class="sac-title">Q-Commerce Behavioral Analytics Dashboard</span>
    <p class="sac-subtitle">Powered by SAP Analytics Cloud · Team Real Madrid · Mumbai</p>
  </div>
  <div style="text-align:right">
    <span class="filter-pill">🎛️ {zone_f} &nbsp;·&nbsp; {time_f} &nbsp;·&nbsp; {cat_f}</span><br>
    <span style="color:#4A6FA5;font-size:10px">All KPIs, charts &amp; insights respond to every filter</span>
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
# TAB 1
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    kpi_row(
        kpi("Total Sessions",  f"{sessions:,}", f"{zone_f} · {time_f}", "up"),
        kpi("Avg Cart Value",  f"₹{cart_val}",  f"+₹{cross_pct} cross-sell lift", "up", "gold"),
        kpi("Abandonment Rate",f"{ab_rate}%",   f"Target <45% · {time_f}", "down", "warn"),
        kpi("Cross-sell Conv.", f"{cross_pct}%", f"Best: {top_cat} @ {top_pct}%", "up", "green"),
    )
    c1, c2 = st.columns([1.4, 1])
    with c1:
        slbl("Order Volume by Time Window & Category · <em>SAC Story</em>")
        fig1 = go.Figure()
        for cat, vals in vol_data.items():
            fig1.add_bar(name=cat, x=TIME_WINS, y=vals,
                         marker_color=CAT_COL.get(cat, CO),
                         marker_cornerradius=3, marker_line_width=0)
        fig1.update_layout(barmode="stack", height=265, xaxis=ax(), yaxis=ax(grid=True),
                           **mk_layout())
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar":False})
        badge(*ins_vol(zone_f, time_f, cat_f))

    with c2:
        slbl("Session Duration Distribution · <em>SAC Story</em>")
        zm = ZONE_MULT[zone_f]
        dur_v = [round(v * zm) for v in [18000,24000,22000,28000,10000]]
        fig2 = go.Figure(go.Bar(
            x=["0–60s","60–120s","120–180s","180–240s","240s+"], y=dur_v,
            marker_cornerradius=3, marker_line_width=0,
            marker_color=[CT, CGR, CG, CR, CB]
        ))
        fig2.update_layout(height=250, showlegend=False, xaxis=ax(), yaxis=ax(grid=True),
                           **mk_layout())
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        badge("red", "⚠ Sessions >180s carry 70% abandonment risk — reduce choice complexity")

    c3, c4 = st.columns(2)
    with c3:
        slbl("Category Share by Order Volume · <em>SAC Story</em>")
        if cat_f == "All Categories":
            pl = ["Snacks & Bev","Fresh Produce","Dairy","Staples","Frozen","Personal Care"]
            pv = [28,22,14,19,9,8]
        else:
            bs = {"Snacks & Beverages":28,"Fresh Produce":22,"Dairy":14,
                  "Staples & Grains":19,"Frozen Foods":9,"Personal Care":8}
            s = bs.get(cat_f, 15)
            pl, pv = [cat_f,"All Others"], [s, 100-s]
        fig3 = go.Figure(go.Pie(
            labels=pl, values=pv, hole=0.55, marker_colors=CPAL,
            textinfo="label+percent", textfont=dict(size=11, color="#FFFFFF"),
            marker=dict(line=dict(color="#0D1B2A", width=2))
        ))
        fig3.update_layout(height=235, showlegend=False, **mk_layout())
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    with c4:
        slbl("Cross-sell Conversion by Bundle · <em>SAC KPI</em>")
        cc = [CT if v>=35 else CG if v>=25 else CR for v in cross_ch]
        fig4 = go.Figure(go.Bar(
            y=["Snacks + Bev","Dairy + Breakfast","Frozen + Snacks","Grains + Staples","Personal + Bev"],
            x=cross_ch, orientation="h", marker_color=cc,
            marker_cornerradius=3, marker_line_width=0,
            text=[f"{v}%" for v in cross_ch], textposition="outside",
            textfont=dict(size=11, color="#D0E4F0")
        ))
        fig4.update_layout(height=235, showlegend=False, xaxis=ax("%"), yaxis=ax(),
                           **mk_layout())
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 2
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    kpi_row(
        kpi("Highest Abandon Rate", f"{top_ab_val}%",   f"{top_ab_cat} · {zone_f}",    "down","warn"),
        kpi("Avg Drop-off Session", f"{avg_sess}s",      f"Threshold 180s · {time_f}",  "down","warn"),
        kpi("Recovery Opportunity", f"₹{recovery}L/mo", "If abandonment → 45%",         "up",  "gold"),
        kpi("Overall Abandon Rate", f"{ab_rate}%",       f"{cat_f} · {zone_f}",          "down","warn"),
    )
    c1, c2 = st.columns(2)
    with c1:
        slbl("Conversion Funnel — All Sessions · <em>SAC Story</em>")
        fig5 = go.Figure(go.Funnel(
            y=["App Sessions","Product Views","Add to Cart","Checkout Start","Order Complete"],
            x=funnel_v, textinfo="value+percent initial",
            marker=dict(color=["#1E3A5F",CT,CGR,CG,CR],
                        line=dict(color="#0D1B2A", width=1)),
            connector=dict(line=dict(color="#1E3A5F", width=2))
        ))
        # Funnel uses mk_layout() — no duplicate font key
        fig5.update_layout(height=295, **mk_layout())
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar":False})
        badge(*ins_funnel(zone_f, time_f, completion))

    with c2:
        slbl("Abandonment Rate by Category · <em>SAC Dashboard</em>")
        abc = [CR if v>50 else CG if v>35 else CT for v in ab_vals]
        fig6 = go.Figure(go.Bar(
            y=ab_labs, x=ab_vals, orientation="h",
            marker_color=abc, marker_cornerradius=3, marker_line_width=0,
            text=[f"{v}%" for v in ab_vals], textposition="outside",
            textfont=dict(size=11, color="#D0E4F0")
        ))
        fig6.update_layout(height=295, showlegend=False, xaxis=ax("%"), yaxis=ax(),
                           **mk_layout())
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar":False})
        badge(*ins_abandon(zone_f, time_f, cat_f, top_ab_cat, top_ab_val))

    slbl("Abandonment Rate by Time Window & Zone · <em>SAC Story</em>")
    zs = [zone_f] if zone_f != "All Zones" else ZONES
    ts = [time_f] if time_f != "All Windows" else TIME_WINS
    twc = [CB, CT, CGR, CG, CR, "#FF4444"]
    fig7 = go.Figure()
    for tw in ts:
        ti = TW_IDX[tw]
        rv = [min(95, round(sum(ABANDON[c][z] for c in CATEGORIES)/len(CATEGORIES)) + TW_AB[tw])
              for z in zs]
        fig7.add_bar(name=tw, x=zs, y=rv,
                     marker_color=twc[ti], marker_cornerradius=2, marker_line_width=0)
    fig7.update_layout(barmode="group", height=230, yaxis=ax("%", grid=True), xaxis=ax(),
                       **mk_layout())
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar":False})

# ════════════════════════════════════════════════════════════════════════════
# TAB 3
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    kpi_row(
        kpi("Model Accuracy",    f"{model_acc}%",   f"Smart Predict · {zone_f}",      "up"),
        kpi("Top Cross-sell",    top_cat,           f"{top_pct}% conv · {time_f}",    "up",  "gold"),
        kpi("Churn-Risk Users",  f"{churn_cnt:,}",  f"{cat_f} · {zone_f}",            "down","warn"),
        kpi("Best Intervention", best_tw,           f"{best_score}% intent score",    "up",  "green"),
    )
    c1, c2 = st.columns([1.1, 1])
    with c1:
        slbl("Predicted Cross-sell Conversion Probability · <em>Smart Predict</em>")
        pc = [CT if v>=60 else CG if v>=40 else CR for v in pred_vals]
        fig8 = go.Figure(go.Bar(
            y=p_cats, x=pred_vals, orientation="h",
            marker_color=pc, marker_cornerradius=4, marker_line_width=0,
            text=[f"{v}%" for v in pred_vals], textposition="outside",
            textfont=dict(size=12, color="#D0E4F0")
        ))
        fig8.add_vline(x=50, line_dash="dash", line_color=CR, line_width=1.5,
                       annotation_text="50% threshold",
                       annotation_font=dict(color=CR, size=10))
        fig8.update_layout(height=285, showlegend=False, xaxis=ax("%"), yaxis=ax(),
                           **mk_layout())
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar":False})
        badge(*ins_predict(zone_f, time_f, top_cat, top_pct))

    with c2:
        slbl("Churn Risk Segmentation · <em>Smart Predict</em>")
        fig9 = go.Figure(go.Pie(
            labels=["Low risk","Medium risk","High risk","At-risk returning"],
            values=churn_pie, hole=0.5,
            marker_colors=[CT, CG, CR, CP],
            marker=dict(line=dict(color="#0D1B2A", width=2)),
            textinfo="label+percent", textfont=dict(size=11, color="#FFFFFF"),
            pull=[0,0,0.08,0]
        ))
        fig9.update_layout(height=280, **mk_layout())
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar":False})
        badge("red", f"⚠ {churn_pie[2]}% high-risk in {zone_f} · {cat_f} — send targeted retention offer now")

    slbl("Purchase Intent Score by Time Window · <em>Smart Predict · Behavioral Trigger Index</em>")
    fig10 = go.Figure()
    fig10.add_scatter(
        x=x_int, y=y_int, mode="lines+markers",
        line=dict(color=CT, width=3),
        fill="tozeroy", fillcolor="rgba(47,255,209,0.10)",
        marker=dict(color=CT, size=9, line=dict(color="#0D1B2A", width=2))
    )
    if time_f == "All Windows":
        fig10.add_hrect(y0=75, y1=105, fillcolor="rgba(47,255,209,0.06)", line_width=0,
                        annotation_text="High intent zone",
                        annotation_font=dict(color=CT, size=10),
                        annotation_position="top right")
    fig10.update_layout(height=210, showlegend=False,
                        yaxis={**ax("%", grid=True), "range":[0,105]}, xaxis=ax(),
                        **mk_layout())
    st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar":False})
    badge(*ins_predict(zone_f, time_f, best_tw, max(y_int)))

# ════════════════════════════════════════════════════════════════════════════
# TAB 4
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    kpi_row(
        kpi("High Waste Risk Zones", f"{high_risk} / {len(w_zones)}",
            f">60% threshold · {cat_f}", "down","warn"),
        kpi("Projected Waste Saving", f"{waste_sav}%",
            f"{zone_f} · {cat_f}", "up","green"),
        kpi("Perishable Overstock",   f"₹{overstock}L/wk",
            f"{zone_f} · {time_f}", "down","warn"),
        kpi("Planning Version",       "v3 — Active", "SAC Planning live", "up","gold"),
    )
    c1, c2 = st.columns(2)
    with c1:
        slbl("Perishable Waste Risk Score by Zone & Category · <em>SAC Planning</em>")
        fig11 = go.Figure()
        fig11.add_bar(name="Fresh Produce", y=w_zones, x=w_fresh,
                      orientation="h", marker_color=CR,
                      marker_cornerradius=3, marker_line_width=0)
        fig11.add_bar(name="Dairy", y=w_zones, x=w_dairy,
                      orientation="h", marker_color=CG,
                      marker_cornerradius=3, marker_line_width=0)
        fig11.add_vline(x=60, line_dash="dash", line_color="#7ECECA", line_width=1.5,
                        annotation_text="Action threshold (60)",
                        annotation_font=dict(color="#7ECECA", size=10))
        fig11.update_layout(barmode="group", height=290, xaxis=ax(), yaxis=ax(),
                            **mk_layout())
        st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar":False})
        badge(*ins_darkstore(zone_f, cat_f, time_f, waste_sav))

    with c2:
        slbl("Dark Store Inventory vs SAC Demand Forecast · <em>SAC Planning</em>")
        fig12 = go.Figure()
        fig12.add_bar(name="Current Stock (index)", x=w_zones, y=inv_stock,
                      marker_color=CN, marker_cornerradius=3,
                      marker_line_width=0, opacity=0.9)
        fig12.add_bar(name="SAC Demand Forecast", x=w_zones, y=inv_demand,
                      marker_color=CT, marker_cornerradius=3, marker_line_width=0)
        fig12.update_layout(barmode="group", height=275,
                            yaxis=ax(" idx", grid=True), xaxis=ax(),
                            **mk_layout())
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar":False})
        badge("red", f"⚠ {max_gap_z}: {max_gap}% overstock vs SAC behavioral demand forecast · {cat_f}")

    slbl("Procurement Adjustment Recommendations · <em>SAC Planning · Action Trigger</em>")

    def style_pri(val):
        if val=="URGENT":   return "background-color:#2B0A0A;color:#FF9999;font-weight:700"
        if val=="MODERATE": return "background-color:#2B1F00;color:#FFE066;font-weight:700"
        return "background-color:#0A2A2B;color:#2FFFD1;font-weight:700"

    st.dataframe(recs_df.style.applymap(style_pri, subset=["Priority"]),
                 use_container_width=True, hide_index=True, height=220)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sac-footer">
SAP Analytics Cloud &nbsp;·&nbsp; Q-Commerce Behavioral Dataset &nbsp;·&nbsp;
2,00,000+ records &nbsp;·&nbsp; Mumbai Zones &nbsp;·&nbsp;
<strong>Team Real Madrid</strong> &nbsp;·&nbsp;
Active: {zone_f} · {time_f} · {cat_f}
</div>
""", unsafe_allow_html=True)
