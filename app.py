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
    
    # Official Monthly Data for Building 21
    monthly_reviews = [
        {"Month": "March 2026", "Reviews": 58, "Overall Rating": 89.66, "Satisfaction": 90.50, "Cleanliness": 88.75, "Staff": 86.25, "Comfort": 91.25},
        {"Month": "April 2026", "Reviews": 35, "Overall Rating": 93.97, "Satisfaction": 95.17, "Cleanliness": 95.69, "Staff": 90.52, "Comfort": 95.69}
    ]
        
    return {"records": records, "monthly_reviews": monthly_reviews}

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

tab_create, tab_active, tab_history, tab_performance, tab_monthly = st.tabs([
    "🆕 Create Work Order", 
    "🛠️ Active Tasks", 
    "🔍 Room History", 
    "📊 Analytics",
    "📈 Monthly Building Performance"
])

# TAB 1: WORK ORDER CREATION
with tab_create:
    st.header("Log New Work Order")
    with st.form("work_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            room = st.text_input("Room Number:")
            order_type = st.selectbox("Type:", ["Supervisor", "Guest Call"])
            priority = st.selectbox("Priority:", ["Urgent", "Time Queue"])
        with col2:
            dept = st.selectbox("Department:", ["Housekeeping", "Maintenance"])
            assign_to = st.selectbox("Assign To:", STAFF_LIST)
            is_repeat = st.checkbox("Is this a Repeat Call? (-5 Points)")
            
        desc = st.text_area("Request Description:")
        if st.form_submit_button("Dispatch Work Order"):
            new_id = len(db["records"]) + 100
            db["records"].append({
                "id": new_id, "room": room, "type": order_type, "priority": priority,
                "dept": dept, "assigned_to": assign_to, "desc": desc,
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "started_at": "", "completed_at": "", "comp_notes": "",
                "status": "Pending", "is_repeat": is_repeat, "points": 0, "guest_review": None
            })
            st.success(f"✅ Dispatched Order #{new_id} to {assign_to}!")
            st.rerun()

# TAB 2: ACTIVE TASKS & WORK COMPLETION
with tab_active:
    st.header("Staff Execution Hub")
    filter_staff = st.selectbox("View Queue For:", ["All Staff"] + STAFF_LIST)
    
    filtered_orders = [o for o in db["records"] if (filter_staff == "All Staff" or o.get("assigned_to") == filter_staff) and o.get("status") != "Completed"]
    
    if not filtered_orders:
        st.info("🎉 Current queue cleared.")
    else:
        for order in filtered_orders:
            with st.container():
                st.markdown(f"### Work Order #{order['id']} - Room {order['room']}")
                st.write(f"**Assigned:** {order.get('assigned_to', 'N/A')} | **Type:** {order.get('type', 'N/A')}")
                
                if order["status"] == "Pending":
                    if st.button(f"▶️ Start Task #{order['id']}", key=f"s_{order['id']}"):
                        order["status"] = "In Progress"
                        st.rerun()
                elif order["status"] == "In Progress":
                    if st.button(f"🏁 Complete Task #{order['id']}", key=f"c_{order['id']}"):
                        order["status"] = "Completed"
                        order["points"] = 10
                        st.rerun()
            st.markdown("---")

# TAB 3: UNIT HISTORY SEARCH
with tab_history:
    st.header("Unit History & Trends")
    search_room = st.text_input("🔍 Search by Room/Unit Number:")
    if search_room:
        history = [o for o in db["records"] if search_room.lower() in o.get("room", "").lower()]
        if not history:
            st.warning("No previous work orders found.")
        else:
            st.dataframe(pd.DataFrame(history)[["id", "room", "assigned_to", "status"]], use_container_width=True)

# TAB 4: PERFORMANCE ANALYTICS & HEATMAP
with tab_performance:
    st.header("Team Performance & Building Health")
    
    st.subheader("🏢 Thermal Building Heatmap (Work Order Volume)")
    floor_counts = [get_floor(o.get("room", "0")) for o in db["records"]]
    df_counts = pd.DataFrame({"Floor": floor_counts}).value_counts().reset_index()
    df_counts.columns = ["Floor", "Orders"]
    
    building_floors = [14, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    df_map = pd.DataFrame({"Floor": building_floors}).merge(df_counts, on="Floor", how="left").fillna(0)
    
    df_map["Zone"] = df_map["Floor"].apply(lambda f: "Zone 2" if f >= 7 else "Zone 1")
    df_map["Floor_Label"] = "Floor " + df_map["Floor"].astype(str)
    
    heatmap = alt.Chart(df_map).mark_rect(stroke='white', strokeWidth=2).encode(
        y=alt.Y('Floor:O', sort=building_floors, title="Building Level", axis=alt.Axis(labelAngle=0)),
        x=alt.X('Zone:N', title="Maintenance Zone", axis=alt.Axis(labelAngle=0)),
        color=alt.Color('Orders:Q', scale=alt.Scale(scheme='spectral', reverse=True), title='Total Orders'),
        tooltip=['Floor_Label', 'Zone', 'Orders']
    ).properties(height=450)
    
    st.altair_chart(heatmap, use_container_width=True)

# TAB 5: MONTHLY BUILDING PERFORMANCE (UPDATED LAYOUT)
with tab_monthly:
    st.header("Building 21 Monthly Guest Reviews")
    st.caption("Tracking Booking.com average sentiment and operational scores over time.")
    
    df_reviews = pd.DataFrame(db["monthly_reviews"])
    
    # Optimized and compact Bar Chart
    st.subheader("📊 Performance Growth (March vs. April)")
    df_melted = df_reviews.melt(
        id_vars=["Month"], 
        value_vars=["Overall Rating", "Cleanliness", "Staff", "Comfort", "Satisfaction"], 
        var_name="Metric", 
        value_name="Score"
    )
    
    bar_chart = alt.Chart(df_melted).mark_bar().encode(
        # Keep metrics on x-axis to align with table columns
        x=alt.X('Metric:N', title=None, axis=alt.Axis(labelAngle=0, labelFontWeight='bold', labelFontSize=12)),
        # Bars side-by-side by Month
        xOffset='Month:N',
        y=alt.Y('Score:Q', scale=alt.Scale(domain=[80, 100]), title="Average Score"),
        # Color by Month for quick comparison
        color=alt.Color('Month:N', scale=alt.Scale(range=['#0A3161', '#FF7A00']), legend=alt.Legend(title="Report Month", orient="top")),
        tooltip=['Month', 'Metric', 'Score']
    ).properties(height=300) # Compact height
    
    # Force alignment with the table by using the full container width
    st.altair_chart(bar_chart, use_container_width=True)
    
    # Stretched Data Table to match chart width
    st.subheader("📄 Official Report Data")
    st.dataframe(df_reviews, use_container_width=True, hide_index=True)
    
    # Form to inject new monthly data
    st.markdown("---")
    with st.expander("➕ Log Upcoming Monthly Report"):
        with st.form("new_month_form"):
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                new_month = st.text_input("Month (e.g. May 2026)")
                new_reviews = st.number_input("Number of Reviews", min_value=0, value=0)
            with col_m2:
                new_rating = st.number_input("Overall Rating", min_value=0.0, max_value=100.0, value=0.0)
                new_sat = st.number_input("Overall Satisfaction", min_value=0.0, max_value=100.0, value=0.0)
            with col_m3:
                new_clean = st.number_input("Cleanliness Rating", min_value=0.0, max_value=100.0, value=0.0)
                new_staff = st.number_input("Staff Rating", min_value=0.0, max_value=100.0, value=0.0)
                new_comf = st.number_input("Comfort Rating", min_value=0.0, max_value=100.0, value=0.0)
                
            if st.form_submit_button("Save Report to Database"):
                if new_month:
                    db["monthly_reviews"].append({
                        "Month": new_month, "Reviews": new_reviews, "Overall Rating": new_rating, 
                        "Satisfaction": new_sat, "Cleanliness": new_clean, "Staff": new_staff, "Comfort": new_comf
                    })
                    st.success(f"{new_month} data saved!")
                    st.rerun()
