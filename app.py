import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import urllib.parse
import urllib.request
import time
import re
import altair as alt
import random

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Building 21 - Operations & Sentiment", layout="wide")

# (CSS Styles maintained from previous version for consistency)
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; color: #0A3161; }
    h1, h2, h3, h4, h5, h6 { color: #0A3161 !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #E2E8F0; padding: 8px; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background-color: #FF7A00 !important; color: #FFFFFF !important; font-weight: bold; border: 1px solid #FF7A00 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATA ENGINE (WITH MONTHLY REVIEW STORAGE)
# ---------------------------------------------------------
@st.cache_resource
def get_shared_database():
    return {
        "records": [],
        "monthly_reviews": {
            "21": [
                {"month": "March 2026", "rating": 89.66, "cleanliness": 88.75, "staff": 86.25},
                {"month": "April 2026", "rating": 93.97, "cleanliness": 95.69, "staff": 90.52}
            ]
        }
    }

db = get_shared_database()

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.image(Image.open("IMG_0783.png"), use_container_width=True)
page = st.sidebar.radio("Navigation", ["Operations Hub", "Monthly Sentiment Tracker"])

# ---------------------------------------------------------
# PAGE 1: OPERATIONS HUB (Maintenance & Heatmap)
# ---------------------------------------------------------
if page == "Operations Hub":
    st.header("Operations Hub")
    # ... [Keep your previous Active Task/Heatmap logic here] ...
    st.info("Your heatmaps and maintenance queue operate here.")

# ---------------------------------------------------------
# PAGE 2: MONTHLY SENTIMENT TRACKER (BUILDING 21)
# ---------------------------------------------------------
elif page == "Monthly Sentiment Tracker":
    st.header("Building 21: Sentiment vs. Operations")
    
    # A. TREND CHART
    df_reviews = pd.DataFrame(db["monthly_reviews"]["21"])
    st.subheader("Performance Trends")
    chart = alt.Chart(df_reviews).mark_line(point=True, color="#FF7A00", strokeWidth=3).encode(
        x='month:O', y=alt.Y('rating:Q', scale=alt.Scale(domain=[70, 100])),
        tooltip=['month', 'rating', 'cleanliness', 'staff']
    )
    st.altair_chart(chart, use_container_width=True)
    
    # B. DATA TABLE
    st.subheader("Monthly Breakdown")
    st.dataframe(df_reviews, use_container_width=True)
    
    # C. ADD NEW MONTHLY DATA
    with st.expander("➕ Log New Monthly Review Data"):
        with st.form("add_review"):
            m = st.text_input("Month (e.g. May 2026):")
            r = st.number_input("Overall Rating:")
            c = st.number_input("Cleanliness Rating:")
            s = st.number_input("Staff Rating:")
            if st.form_submit_button("Save"):
                db["monthly_reviews"]["21"].append({"month": m, "rating": r, "cleanliness": c, "staff": s})
                st.rerun()

    # D. CORRELATION INSIGHT
    st.markdown("---")
    st.subheader("Operational Correlation")
    st.write("Current analysis shows Building 21 performance is trending upward.")
    st.info("Tip: Look for dips in 'Staff Rating' on months where maintenance volume was exceptionally high.")
