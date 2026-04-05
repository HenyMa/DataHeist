import streamlit as st
import base64
import pandas as pd
import plotly.graph_objects as go
from predict import predict_risk

# Page config
st.set_page_config(
    page_title="Home Investment Guide",
    page_icon="🏠",
    layout="wide",
)

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
    .block-container {{ max-width: 900px; padding-top: 2rem; }}
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
    .risk-low  {{ background-color: #186B3B; color: #ffffff; }}
    .risk-med  {{ background-color: #A36F07; color: #000000; }}
    .risk-high {{ background-color: #8F0303; color: #ffffff; }}
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
    div[data-testid="stButton"] > button[kind="primary"] {{
        background-color: #1a6bbf !important;
        border-color: #1a6bbf !important;
        color: #ffffff !important;
    }}
    div[data-testid="stButton"] > button[kind="primary"]:hover {{
        background-color: #155a9e !important;
        border-color: #155a9e !important;
    }}
    button[data-baseweb="tab"] {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
    }}
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stSelectbox"] > div > div > div {{
        border-radius: 0 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<h1 style="color:black;">Home Investment Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:black;">Assess the investment risk of a property based on local migration and price trends</p>', unsafe_allow_html=True)
st.divider()

# Tabs
tab_predict, tab_map = st.tabs(["Prediction", "Interactive Map"])

#  Prediction tab
with tab_predict:
    mode = st.selectbox(
        "Select your perspective",
        options=["First-time Buyer", "City Council Member", "Investor"],
        help="Choose the perspective you want the analysis for"
    )
    st.markdown(f"<p style='color:black; font-weight:600; margin-top:0.2rem;'>Selected Mode: {mode}</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        high_price = st.number_input(
            "High Price ($)",
            min_value=0.0,
            value=500000.0,
            step=1000.0,
            format="%.2f",
            help="Upper bound of the local housing price range",
        )

    with col2:
        low_price = st.number_input(
            "Low Price ($)",
            min_value=0.0,
            value=250000.0,
            step=1000.0,
            format="%.2f",
            help="Lower bound of the local housing price range",
        )

    col3, col4 = st.columns(2)

    with col3:
        moves_out = st.number_input(
            "Moves Out",
            min_value=0,
            value=1200,
            step=1,
            help="Number of residents who moved out of the area",
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

    if st.button("Calculate Risk", type="primary", use_container_width=True):
        result = predict_risk(low_price, high_price, moves_in, moves_out)
        probs = result["probabilities"]
        risk_pct = round(result["risk_pct"], 1)

        if mode == "First-time Buyer":
            low_label, med_label, high_label = "Buy now!", "Moderate (be cautious)", "Too risky (consider renting)"
            low_rec = "This neighborhood looks chill AF. A great place to hang it up!"
            med_rec = "The market here is mixed. Make sure you can handle potential fluctuations before committing."
            high_rec = "Prices and population trends suggest instability. Renting may be a smarter move right now."
        elif mode == "City Council Member":
            low_label, med_label, high_label = "Keep up the good work, big dawg!", "Monitor", "Urgent intervention"
            low_rec = "This area is lit AF rn. Current policies appear to be working well!"
            med_rec = "Some warning signs in migration and pricing. Keep a close eye and be ready to act."
            high_rec = "Significant population outflow and market stress detected. Immediate policy action is needed."
        else:  # Investor
            low_label, med_label, high_label = "Invest", "Look out", "Avoid"
            low_rec = "Strong demand and favorable migration trends. INVEST in this place rn!"
            med_rec = "Mixed signals in the market. Proceed carefully and hedge your exposure."
            high_rec = "High risk of value decline with weak demand. Capital is better deployed elsewhere."

        if risk_pct < 33:
            css_class = "risk-low"
            status_text = low_label
            recommendation = low_rec
        elif risk_pct < 67:
            css_class = "risk-med"
            status_text = med_label
            recommendation = med_rec
        else:
            css_class = "risk-high"
            status_text = high_label
            recommendation = high_rec

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

# Interactive Map tab
with tab_map:
    @st.cache_data
    def load_map_data():
        df = pd.read_csv("zip_flight_risk_scores.csv")
        def get_color(score):
            if score > 0.67:
                return "#e63946"
            elif score >= 0.33:
                return "#f4a236"
            else:
                return "#2ec47a"

        def get_label(score):
            if score > 0.67:
                return "Risky"
            elif score >= 0.33:
                return "Moderate"
            else:
                return "Safe"

        df["color"] = df["flight_risk_score"].apply(get_color)
        df["label"] = df["flight_risk_score"].apply(get_label)
        df["risk_pct"] = (df["flight_risk_score"] * 100).round(1)
        return df

    map_df = load_map_data()

    fig = go.Figure()

    for tier in ["Risky", "Moderate", "Safe"]:
        group = map_df[map_df["label"] == tier]
        if group.empty:
            continue
        fig.add_trace(go.Scatter(
            x=group["ZipCode_Longitude"],
            y=group["ZipCode_Latitude"],
            mode="markers+text",
            name=tier,
            marker=dict(
                color=group["color"],
                size=16,
                opacity=0.85,
                line=dict(color="white", width=0.6),
            ),
            text=group["ZipCode"].astype(str),
            textposition="middle center",
            textfont=dict(size=5, color="white", family="Arial Black"),
            customdata=list(zip(
                group["ZipCode"],
                group["risk_pct"],
                group["label"],
                group["pct_leave"].mul(100).round(1),
                group["net_migration_rate"].mul(100).round(1),
                group["median_value"],
            )),
            hovertemplate=(
                "<b>ZIP %{customdata[0]}</b><br>"
                "Flight Risk: %{customdata[1]}%<br>"
                "Status: <b>%{customdata[2]}</b><br>"
                "% Leaving: %{customdata[3]}%<br>"
                "Net Migration Rate: %{customdata[4]}%<br>"
                "Median Value: $%{customdata[5]:,.0f}<extra></extra>"
            ),
        ))

    fig.update_layout(
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(color="white"),
        title=dict(text=""),
        xaxis=dict(
            title="Longitude",
            color="#8b8fa3",
            gridcolor="#222",
            showgrid=True,
        ),
        yaxis=dict(
            title="Latitude",
            color="#8b8fa3",
            gridcolor="#222",
            showgrid=True,
            scaleanchor="x",
            scaleratio=1,
        ),
        legend=dict(
            bgcolor="#1a1d27",
            bordercolor="#333",
            borderwidth=1,
            font=dict(color="white"),
            title=dict(text="Risk Level", font=dict(color="white")),
        ),
        margin=dict(l=40, r=20, t=20, b=40),
        height=720,
        hoverlabel=dict(
            bgcolor="#1a1d27",
            bordercolor="#444",
            font=dict(color="white", size=12),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Click a circle to select it. Hover to see ZIP code details including flight risk % and status")

# Footer
st.divider()
st.markdown('<p style="color:blue;">Analysis based on historical migration patterns and local market indicators. Big thanks to Melissa for the datasets! Take caution with these predictions ofc...</p>', unsafe_allow_html=True)
