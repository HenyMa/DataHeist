import streamlit as st
import requests

# Page Config
st.set_page_config(
    page_title="Migration Risk Estimator",
    page_icon="📊",
    layout="centered",
)

# Custom styling
st.markdown(
    """
    <style>
    .block-container { max-width: 640px; padding-top: 2rem; }
    .risk-box {
        padding: 1.5rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 1rem;
    }
    .risk-low  { background-color: #d4edda; color: #155724; }
    .risk-med  { background-color: #fff3cd; color: #856404; }
    .risk-high { background-color: #f8d7da; color: #721c24; }
    .risk-pct  { font-size: 2.4rem; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.title("📊 Migration Risk Estimator")
st.caption("Estimate the probability of net out-migration for the coming year.")

st.divider()

# Inputs
col1, col2 = st.columns(2)

with col1:
    high_price = st.number_input(
        "High Price ($)",
        min_value=0.0,
        value=500000.0,
        step=1000.0,
        format="%.2f",
        help="Upper bound of the local housing price range.",
    )

with col2:
    low_price = st.number_input(
        "Low Price ($)",
        min_value=0.0,
        value=250000.0,
        step=1000.0,
        format="%.2f",
        help="Lower bound of the local housing price range.",
    )

col3, col4 = st.columns(2)

with col3:
    moves_out = st.number_input(
        "Moves Out",
        min_value=0,
        value=1200,
        step=1,
        help="Number of residents who moved out of the area.",
    )

with col4:
    moves_in = st.number_input(
        "Moves In",
        min_value=0,
        value=1000,
        step=1,
        help="Number of residents who moved into the area.",
    )

st.divider()

# Predict
BACKEND_URL = "http://localhost:8000/predict"  # ← point to your backend

if st.button("Calculate Risk", type="primary", use_container_width=True):
    payload = {
        "high_price": high_price,
        "low_price": low_price,
        "moves_out": moves_out,
        "moves_in": moves_in,
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        response.raise_for_status()
        risk_pct = response.json().get("risk_pct", 0.0)
    except Exception:
        # if backend is unreachable
        st.warning(
            "⚠️ Could not reach the backend. Showing a placeholder calculation.",
            icon="🔌",
        )
        # Placeholder
        net = moves_out - moves_in
        ratio = net / max(moves_in, 1)
        price_gap = (high_price - low_price) / max(high_price, 1)
        risk_pct = round(min(max((ratio * 50) + (price_gap * 20), 0), 100), 1)

    # Display result
    if risk_pct < 30:
        css_class = "risk-low"
        emoji = "✅"
    elif risk_pct < 60:
        css_class = "risk-med"
        emoji = "⚠️"
    else:
        css_class = "risk-high"
        emoji = "🚨"

    st.markdown(
        f"""
        <div class="risk-box {css_class}">
            <div>{emoji}</div>
            <div class="risk-pct">{risk_pct}%</div>
            <div style="margin-top:.4rem; font-size:1.1rem;">
                You have a <strong>{risk_pct}%</strong> risk of net out-migration next year.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Footer
st.divider()
st.caption(
    "This tool sends inputs to a backend model for prediction. "
    "Update `BACKEND_URL` to point to your deployed endpoint."
)
