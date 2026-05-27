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
# 1. PAGE CONFIGURATION & CORPORATE BRAND DESIGN THEME
# ---------------------------------------------------------
st.set_page_config(page_title="Building 21 - Work Order Management", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; color: #0A3161; }
    h1, h2, h3, h4, h5, h6 { color: #0A3161 !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #E2E8F0; padding: 8px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #0A3161 !important; background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 16px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background-color: #FF7A00 !important; color: #FFFFFF !important; font-weight: bold; border: 1px solid #FF7A00 !important; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea { border-color: #0A3161 !important; color: #0A3161 !important; }
    div.stButton > button { background-color: #0A3161 !important; color: #FFFFFF !important; font-weight: bold !important; border: 2px solid #0A3161 !important; border-radius: 6px !important; padding: 10px; width: 100%; }
    div.stButton > button:hover { background-color: #FF7A00 !important; color: #FFFFFF !important; border: 2px solid #FF7A00 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER LOGIC: SMART FLOOR EXTRACTOR
# ---------------------------------------------------------
def get_floor(room_string):
    matches = re.findall(r'\d+', str(room_string))
    if not matches: return 0
    last_num = int(matches[-1])
    floor = last_num // 100 if last_num >= 100 else 1 
    if floor == 13: return 14
    return floor

# ---------------------------------------------------------
# 2. FREE CENTRAL SYNC DATABASE ENGINE
# ---------------------------------------------------------
@st.cache_resource
def get_shared_database():
    records = []
    # Mock data to populate your heatmap
    for i in range(40):
        fl = random.choice([1, 2, 3, 4, 6] if random.random() > 0.3 else [8, 11, 12, 14])
        records.append({"id": i, "room": f"{fl}{random.randint(10, 25)}", "status": "Pending", "assigned_to": "Stephen S.", "points": 0})
    return {"records": records}

db = get_shared_database()
STAFF_LIST = ["James W.", "Stephen S.", "Miguel V.", "Mike R.", "Johanna M.", "Silvia M.", "Dispatch 1"]

# ---------------------------------------------------------
# 3. GUEST REVIEW PORTAL (HIDES MAIN APP)
# ---------------------------------------------------------
if "review" in st.query_params:
    st.markdown("<h2 style='text-align: center; color: #0A3161;'>Building 21 Guest Feedback</h2>", unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# 4. STAFF HUB
# ---------------------------------------------------------
try:
    with st.columns([1, 4, 1])[1]:
        st.image(Image.open("IMG_0783.png"), use_container_width=True)
except: pass

st.markdown("<h3 style='text-align: center; color: #0A3161;'>SYNCED WORK ORDER HUB</h3>", unsafe_allow_html=True)

tab_create, tab_active, tab_history, tab_performance = st.tabs(["🆕 Create", "🛠️ Active", "🔍 History", "📊 Analytics"])

with tab_create:
    with st.form("wo", clear_on_submit=True):
        room = st.text_input("Room Number:")
        if st.form_submit_button("Dispatch"):
            db["records"].append({"id": len(db["records"])+1, "room": room, "status": "Pending", "assigned_to": "James W."})
            st.rerun()

with tab_active:
    for order in db["records"]:
        if order["status"] != "Completed":
            st.write(f"Room {order['room']} - {order['status']}")

with tab_history:
    st.header("Unit History")
    search = st.text_input("Search Room:")
    if search:
        st.write([o for o in db["records"] if search in o["room"]])

with tab_performance:
    st.header("Team Performance & Building Health")
    
    # Heatmap Logic
    floor_counts = [get_floor(o["room"]) for o in db["records"]]
    df_counts = pd.DataFrame({"Floor": floor_counts}).value_counts().reset_index()
    df_counts.columns = ["Floor", "Orders"]
    
    building_floors = [14, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    df_map = pd.DataFrame({"Floor": building_floors}).merge(df_counts, on="Floor", how="left").fillna(0)
    
    df_map["Zone"] = df_map["Floor"].apply(lambda f: "Zone 2" if f >= 7 else "Zone 1")
    tech_map = {"Zone 1": "Stephen S., Mike R.", "Zone 2": "James W., Miguel V."}
    df_map["Technicians"] = df_map["Zone"].map(tech_map)
    df_map["Floor_Label"] = "Floor " + df_map["Floor"].astype(str)
    
    heatmap = alt.Chart(df_map).mark_rect(stroke='white', strokeWidth=2).encode(
        y=alt.Y('Floor:O', sort=building_floors, title="Level"),
        x=alt.X('Zone:N', title="Zone"),
        color=alt.Color('Orders:Q', scale=alt.Scale(scheme='spectral', reverse=True)),
        tooltip=['Floor_Label', 'Zone', 'Technicians', 'Orders']
    )
    st.altair_chart(heatmap, use_container_width=True)
