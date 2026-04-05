import streamlit as st
import base64
from predict import predict_risk

# Page config
st.set_page_config(
    page_title="Home Investment Guide",
    page_icon="🏠",
    layout="centered",
)

# Helper: load image
@st.cache_data
def get_image_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

bg_image = get_image_base64("hq720.jpg")

# Custom styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(245, 247, 250, 0.72), rgba(245, 247, 250, 0.72)),
                    url("data:image/jpeg;base64,{bg_image}") center / cover fixed no-repeat;
    }}
    .block-container {{ max-width: 640px; padding-top: 2rem; }}
    .risk-box {{
        padding: 1.5rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 1rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }}
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] {{
        backdrop-filter: blur(2px);
    }}
    .risk-low  {{ background-color: #007f33; color: #ffffff; }}
    .risk-med  {{ background-color: #cca300; color: #000000; }}
    .risk-high {{ background-color: #b30000; color: #ffffff; }}
    .risk-pct  {{ font-size: 2.4rem; font-weight: 700; }}
    .prob-bar  {{ display: flex; gap: .5rem; margin-top: 1rem; }}
    .prob-item {{ flex: 1; padding: .6rem; border-radius: 8px; text-align: center; font-size: .85rem; }}
    div[data-testid="stNumberInput"] label {{
        color: black !important;
        font-weight: 600;
        font-size: 1rem; 
    }}
    div[data-testid="stForm"] label[for="Select your perspective"] {{
        color: black !important;
        font-weight: 600;
        margin-bottom: 0.1rem;
        font-size: 1rem;
    }}
    div[data-testid="stSelectbox"] {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.3rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<h1 style="color:black;">Home Investment Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:black;">Assess the investment risk of a property based on local migration trends.</p>', unsafe_allow_html=True)
st.divider()

# Mode selection
mode = st.selectbox(
    "Select your perspective",
    options=["First-time Buyer", "City Council Member", "Investor"],
    help="Choose the perspective you want the analysis for."
)
st.markdown(f"<p style='color:black; font-weight:600; margin-top:0.2rem;'>Selected Mode: {mode}</p>", unsafe_allow_html=True)
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

# Predict & Display
if st.button("Calculate Risk", type="primary", use_container_width=True):
    result = predict_risk(low_price, high_price, moves_in, moves_out)
    probs = result["probabilities"]  
    risk_pct = round(result["risk_pct"], 1)

    if risk_pct < 33:
        css_class = "risk-low"
        status_text = "Safe to buy"
        recommendation = "This appears to be a solid investment opportunity."
    elif risk_pct < 67:
        css_class = "risk-med"
        status_text = "Caution advised"
        recommendation = "Proceed with caution. Consider further research."
    else:
        css_class = "risk-high"
        status_text = "Too risky to buy"
        recommendation = "High risk of value decline. Consider looking elsewhere."

    # Main risk box
    st.markdown(
        f"""
        <div class="risk-box {css_class}">
            <div style="font-size:1rem; font-weight:600; letter-spacing:.02em;">{status_text}</div>
            <div class="risk-pct">{risk_pct}%</div>
            <div style="margin-top:.4rem; font-size:1rem;">
                {recommendation}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Risk breakdown with check mark
    highest_idx = probs.index(max(probs))
    risk_labels = ["Low Risk", "Medium Risk", "High Risk"]
    css_classes = ["risk-low", "risk-med", "risk-high"]

    st.markdown(
        f"""
        <div class="prob-bar">
            {"".join([
                f'<div class="prob-item {css_classes[i]}">'
                f'<strong>{risk_labels[i]}</strong><br>'
                f'{"✔️" if i == highest_idx else ""}'
                f'</div>'
                for i in range(3)
            ])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Model prediction: **{result['risk']}**")

# Footer
st.divider()
st.markdown('<p style="color:green;">Analysis based on historical migration patterns and local market indicators.</p>', unsafe_allow_html=True)
