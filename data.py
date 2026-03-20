"""
data.py — Mock behavioral dataset for SAC Q-Commerce Dashboard
Team Real Madrid · 200,000+ simulated records
"""

import pandas as pd
import numpy as np
import random


# ── SEED FOR REPRODUCIBILITY ──────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

TIME_LABELS   = ["6–9 AM", "9 AM–12", "12–3 PM", "3–6 PM", "6–10 PM", "10 PM–2 AM"]
ZONES         = ["Andheri", "Bandra", "Powai", "Thane", "Dadar"]
CATEGORIES    = ["Snacks & Beverages", "Fresh Produce", "Dairy",
                 "Staples & Grains", "Frozen Foods", "Personal Care"]
CART_STATUSES = ["Completed", "Abandoned"]
WASTE_RISK    = ["Low", "Medium", "High"]


def get_all_data() -> dict:
    """Return all pre-computed data arrays used by the Streamlit app."""
    return {
        # ── Time-of-day order volumes ──────────────────────────────────────
        "time_labels": TIME_LABELS,
        "snacks":  [120, 180, 210, 260, 320, 480],   # impulse surge late night
        "fresh":   [280, 310, 220, 190, 140,  80],   # morning-heavy
        "staples": [150, 200, 180, 160, 120,  60],

        # ── Session duration (counts per bucket) ──────────────────────────
        "duration_labels": ["0–60s", "60–120s", "120–180s", "180–240s", "240s+"],
        "duration_vals":   [18000,   24000,     22000,      28000,      10000],

        # ── Category share ────────────────────────────────────────────────
        "cat_labels": ["Snacks & Bev", "Fresh Produce", "Staples",
                       "Personal Care", "Frozen", "Other"],
        "cat_data":   [28, 22, 19, 12, 11, 8],

        # ── Cross-sell bundle conversion ──────────────────────────────────
        "cross_labels": ["Snacks + Bev", "Dairy + Breakfast",
                         "Frozen + Snacks", "Grains + Staples", "Personal + Bev"],
        "cross_vals":   [40, 33, 27, 21, 16],

        # ── Cart abandonment by category ──────────────────────────────────
        "abandon_cat_labels": ["Fresh Produce", "Dairy", "Staples",
                               "Frozen", "Snacks", "Personal Care"],
        "abandon_cat_vals":   [58, 52, 49, 38, 24, 18],

        # ── Abandonment heatmap (time × zone) ────────────────────────────
        "abandon_heat_zones": ZONES,
        "abandon_heat_matrix": [
            [55, 48, 41, 52, 44],   # 6–9 AM
            [58, 51, 44, 55, 47],   # 9–12
            [61, 54, 47, 58, 50],   # 12–3
            [64, 57, 50, 61, 53],   # 3–6
            [74, 67, 57, 68, 60],   # 6–10 PM   ← peak risk
            [69, 62, 52, 65, 57],   # 10PM–2AM
        ],

        # ── Smart Predict ─────────────────────────────────────────────────
        "pred_cats": ["Snacks", "Chocolates", "Beverages", "Dairy", "Frozen", "Grains"],
        "pred_vals": [72, 68, 58, 44, 31, 22],

        "churn_labels": ["Low risk", "Medium risk", "High risk", "At-risk returning"],
        "churn_vals":   [12, 28, 38, 22],

        "intent_scores": [42, 55, 60, 58, 78, 88],   # purchase intent by time window

        # ── Dark Store Planning ───────────────────────────────────────────
        "waste_zones":  ZONES,
        "waste_fresh":  [82, 65, 48, 71, 55],
        "waste_dairy":  [68, 52, 38, 62, 45],

        "inv_zones":    ZONES,
        "inv_stock":    [100, 100, 100, 100, 100],    # normalised index
        "inv_demand":   [60,  88,  93,  72,  80],     # SAC forecast index
    }


def generate_raw_csv(n: int = 5000) -> pd.DataFrame:
    """
    Generate a sample raw CSV (5 000 rows by default) that mimics the
    200 000-row dataset used in the SAC Modeler.

    Columns:
        Session_ID, Location_Zone, Time_of_Day, Product_Category,
        Cart_Status, Cart_Value_INR, Session_Duration_Sec,
        Delivery_Time_Min, Waste_Risk_Level, Cross_Sell_Accepted
    """
    # Probability weights that encode the business narrative
    zone_weights    = [0.25, 0.20, 0.15, 0.22, 0.18]
    time_weights    = [0.10, 0.14, 0.16, 0.15, 0.24, 0.21]
    cat_weights     = [0.28, 0.22, 0.14, 0.19, 0.09, 0.08]

    rows = []
    for i in range(n):
        zone     = np.random.choice(ZONES,       p=zone_weights)
        time_win = np.random.choice(TIME_LABELS,  p=time_weights)
        cat      = np.random.choice(CATEGORIES,   p=cat_weights)

        # Abandonment depends on category + time of day
        abandon_base = {
            "Fresh Produce": 0.58, "Dairy": 0.52, "Staples & Grains": 0.49,
            "Frozen Foods": 0.38, "Snacks & Beverages": 0.24, "Personal Care": 0.18
        }[cat]
        if time_win in ["6–10 PM", "10 PM–2 AM"]:
            abandon_prob = abandon_base * 1.18
        elif time_win in ["6–9 AM"]:
            abandon_prob = abandon_base * 0.85
        else:
            abandon_prob = abandon_base
        cart_status = "Abandoned" if random.random() < min(abandon_prob, 0.95) else "Completed"

        # Session duration  (longer → more likely abandoned)
        if cart_status == "Abandoned":
            session_dur = int(np.random.normal(194, 45))
        else:
            session_dur = int(np.random.normal(110, 35))
        session_dur = max(20, session_dur)

        cart_value = int(np.random.normal(312, 80)) if cart_status == "Completed" else int(np.random.normal(180, 60))
        cart_value = max(50, cart_value)

        delivery   = int(np.random.normal(10.5, 2.5))
        delivery   = max(5, min(20, delivery))

        waste_risk = "High" if zone in ["Andheri", "Thane"] and cat in ["Fresh Produce", "Dairy"] else \
                     "Medium" if zone in ["Bandra", "Dadar"] else "Low"

        cross_sell = "Yes" if (cart_status == "Completed" and
                               cat in ["Snacks & Beverages", "Dairy"] and
                               random.random() < 0.40) else "No"

        rows.append({
            "Session_ID":            f"SID{100000 + i}",
            "Location_Zone":         zone,
            "Time_of_Day":           time_win,
            "Product_Category":      cat,
            "Cart_Status":           cart_status,
            "Cart_Value_INR":        cart_value,
            "Session_Duration_Sec":  session_dur,
            "Delivery_Time_Min":     delivery,
            "Waste_Risk_Level":      waste_risk,
            "Cross_Sell_Accepted":   cross_sell,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_raw_csv(5000)
    df.to_csv("sample_dataset.csv", index=False)
    print(f"✅ Generated {len(df)} rows → sample_dataset.csv")
    print(df.head())
    print("\nCart Status distribution:")
    print(df["Cart_Status"].value_counts(normalize=True).map(lambda x: f"{x:.1%}"))
