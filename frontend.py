import streamlit as st
import pickle
import os
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.pkl")

@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

model = load_model()


def predict_risk(low_price, high_price, move_in, move_out):
    avg_price = (low_price + high_price) / 2
    net_flow = move_in - move_out

    median_price = 1_216_000
    relative_price = avg_price / median_price

    input_data = pd.DataFrame(
        [[avg_price, move_out, move_in, net_flow, relative_price]],
        columns=["PropertyValue", "PctLeave", "PctMoveIn", "NetFlow", "RelativePrice"],
    )

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0]

    risk_map = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}

    return {
        "label": risk_map[prediction],
        "prediction": int(prediction),
        "probabilities": probability.tolist(),  # [low, medium, high]
    }


# Page config
st.set_page_config(
    page_title="Migration Risk Estimator",
    page_icon="M",
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
    .prob-bar  { display: flex; gap: .5rem; margin-top: 1rem; }
    .prob-item { flex: 1; padding: .6rem; border-radius: 8px; text-align: center; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.title("Migration Risk Estimator")
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
if st.button("Calculate Risk", type="primary", use_container_width=True):
    result = predict_risk(low_price, high_price, moves_in, moves_out)

    probs = result["probabilities"]  # [low, medium, high]
    # Risk of net out-migration = medium + high probability
    risk_pct = round((probs[1] + probs[2]) * 100, 1)

    if result["prediction"] == 0:
        css_class = "risk-low"
        status_text = "Low risk"
    elif result["prediction"] == 1:
        css_class = "risk-med"
        status_text = "Moderate risk"
    else:
        css_class = "risk-high"
        status_text = "High risk"

    st.markdown(
        f"""
        <div class="risk-box {css_class}">
            <div style="font-size:1rem; font-weight:600; letter-spacing:.02em;">{status_text}</div>
            <div class="risk-pct">{risk_pct}%</div>
            <div style="margin-top:.4rem; font-size:1.1rem;">
                You have a <strong>{risk_pct}%</strong> risk of net out-migration next year.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Breakdown
    st.markdown(
        f"""
        <div class="prob-bar">
            <div class="prob-item risk-low">
                <strong>Low</strong><br>{round(probs[0]*100, 1)}%
            </div>
            <div class="prob-item risk-med">
                <strong>Medium</strong><br>{round(probs[1]*100, 1)}%
            </div>
            <div class="prob-item risk-high">
                <strong>High</strong><br>{round(probs[2]*100, 1)}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Model prediction: **{result['label']}**")

# Footer
st.divider()
st.caption("Powered by a Random Forest classifier trained on OC migration data.")