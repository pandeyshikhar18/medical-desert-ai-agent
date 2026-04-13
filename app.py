import streamlit as st
import pandas as pd
import plotly.express as px

from extractor import extract_dataframe
from scorer import apply_scores, severity
from planner import planner_card

st.set_page_config(layout="wide")
st.title("🚑 Medical Desert Intelligence Dashboard")

# ========================
# SESSION STATE INIT
# ========================
if "data" not in st.session_state:
    st.session_state.data = None

if "facilities" not in st.session_state:
    st.session_state.facilities = None

# ========================
# Upload
# ========================
uploaded = st.file_uploader("Upload Healthcare CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.session_state.data = df

    st.subheader("📄 Raw Dataset")
    st.dataframe(df.head(), use_container_width=True)

    if st.button("🚀 Run AI Agent"):

        facilities = apply_scores(extract_dataframe(df))
        st.session_state.facilities = facilities

# ========================
# USE STORED DATA
# ========================
if st.session_state.facilities:

    facilities = st.session_state.facilities

    result = pd.DataFrame([{
        "name": f.name,
        "score": f.medical_desert_score,
        "severity": severity(f.medical_desert_score),
        "doctors": f.number_doctors,
        "beds": f.capacity,
        "lat": f.latitude,
        "lon": f.longitude
    } for f in facilities])

    # ========================
    # METRICS
    # ========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Facilities", len(result))
    col2.metric("High Risk", len(result[result["score"] > 70]))
    col3.metric("Low Risk", len(result[result["score"] <= 40]))

    st.markdown("---")

    # ========================
    # SEARCH + FILTER
    # ========================
    search = st.text_input("🔍 Search Facility", key="search")

    filtered = result.copy()

    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False)]

    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All", "Severe", "Moderate", "Low"],
        key="filter"
    )

    if severity_filter != "All":
        filtered = filtered[filtered["severity"] == severity_filter]

    # ========================
    # TABLE
    # ========================
    st.subheader("📊 Facility Risk Ranking")

    filtered_sorted = filtered.sort_values(by="score", ascending=False)

    st.dataframe(
        filtered_sorted.style.background_gradient(cmap="Reds"),
        use_container_width=True
    )

    # ========================
    # CHART
    # ========================
    st.subheader("📈 Top Risk Facilities")

    fig = px.bar(
        filtered_sorted.head(10),
        x="name",
        y="score",
        color="severity"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ========================
    # DETAILS
    # ========================
    st.subheader("🔎 Facility Analysis")

    idx = st.selectbox("Select Facility", range(len(facilities)))

    f = facilities[idx]

    st.write("### 🏥", f.name)
    st.write("**Risk Score:**", f.medical_desert_score)
    st.write("**Severity:**", severity(f.medical_desert_score))

    st.write("### 📋 Planner Actions")
    for action in planner_card(f)["actions"]:
        st.write("-", action)

    if f.suspicious_claims:
        st.error("⚠️ Suspicious Claims")
        for s in f.suspicious_claims:
            st.write("-", s)

    st.write("### 📄 Evidence")
    st.info(f.evidence[0].snippet)

    # ========================
    # MAP
    # ========================
    if "lat" in result.columns and "lon" in result.columns:
        st.subheader("🗺️ Geographic Map")

        map_df = result.dropna(subset=["lat", "lon"])

        st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}))

    # ========================
    # DOWNLOAD
    # ========================
    st.download_button(
        "📥 Download Results",
        filtered_sorted.to_csv(index=False),
        "results.csv"
    )