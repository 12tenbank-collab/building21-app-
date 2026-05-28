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
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #E2E8F0; padding: 8px; border-radius: 8px; flex-wrap: wrap; }
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
# HELPER LOGIC: GAUGE BUILDER
# ---------------------------------------------------------
def build_gauge(metric_name, metric_score):
    base_color = "#FF7A00" # Orange for low/caution
    text_color = "#0A3161" # Navy for contrast

    if metric_score >= 90:
        base_color = "#4CAF50" # Green for good
    elif metric_score >= 80:
        base_color = "#FFC107" # Yellow for caution
    
    label_text = f"{metric_score:.1f}%"
    sub_label_text = metric_name

    gauge_html = f"""
    <div style="width: 250px; text-align: center; font-family: sans-serif; display: inline-block; margin: 10px;">
        <svg viewBox="0 0 100 100" width="100%" height="100%">
            <circle cx="50" cy="50" r="45" stroke="#E2E8F0" stroke-width="8" fill="none" stroke-linecap="round"/>
            <circle cx="50" cy="50" r="45" stroke="{base_color}" stroke-width="8" fill="none" stroke-linecap="round"
                    stroke-dasharray="{metric_score*2.827} {2.827 * 100}" stroke-dashoffset="-0.1" transform="rotate(-90 50 50)"/>
            <text x="50" y="55" text-anchor="middle" font-size="20" font-weight="bold" fill="{text_color}">{label_text}</text>
            <text x="50" y="80" text-anchor="middle" font-size="12" fill="{text_color}">{sub_label_text}</text>
        </svg>
    </div>
    """
    return gauge_html

# ---------------------------------------------------------
# 2. FREE CENTRAL SYNC DATABASE ENGINE
# ---------------------------------------------------------
STAFF_LIST = ["James W.", "Stephen S.", "Miguel V.", "Mike R.", "Johanna M.", "Silvia M.", "Dispatch 1"]

@st.cache_resource
def get_shared_database():
    records = []
    for i in range(15):
        fl = random.choice([1, 2, 3, 4, 6] if random.random() > 0.3 else [8, 11, 12, 14])
        is_rep = random.choice([True, False, False, False])
        stat = random.choice(["Pending", "In Progress", "Completed"])
        records.append({
            "id": i + 100, "room": f"{fl}{random.randint(10, 25):02d}", 
            "type": random.choice(["Guest Call", "Supervisor"]), "priority": "Routine",
            "dept": "Maintenance", "assigned_to": random.choice(STAFF_LIST), 
            "desc": "Check AC unit / Plumbing inspection", "created_at": "2026-05-28 08:00:00",
            "started_at": "2026-05-28 08:15:00" if stat != "Pending" else "", 
            "completed_at": "2026-05-28 09:00:00" if stat == "Completed" else "", 
            "comp_notes": "Resolved standard issue" if stat == "Completed" else "",
            "status": stat, "is_repeat": is_rep, "points": 10 if stat == "Completed" else 0, "guest_review": None,
            "sfu_completed": False, "sfu_notes": ""
        })
    
    # Official Monthly Data for Building 21 - Integrated Input Form
    monthly_reviews = pd.DataFrame([
        {"Month": "March 2026", "Reviews": 58, "Overall Rating": 89.66, "Satisfaction": 90.50, "Cleanliness": 88.75, "Staff": 86.25, "Comfort": 91.25},
        {"Month": "April 2026", "Reviews": 35, "Overall Rating": 93.97, "Satisfaction": 95.17, "Cleanliness": 95.69, "Staff": 90.52, "Comfort": 95.69},
        {"Month": "", "Reviews": 0, "Overall Rating": 0.0, "Satisfaction": 0.0, "Cleanliness": 0.0, "Staff": 0.0, "Comfort": 0.0} # Placeholder for new entry
    ])
        
    return {"records": records, "monthly_reviews": monthly_reviews}

db = get_shared_database()

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

tab_create, tab_active, tab_completed, tab_guest, tab_repeats, tab_history, tab_performance, tab_monthly = st.tabs([
    "🆕 Create", 
    "🛠️ Active",
    "✅ Completed",
    "🛎️ Guest Portal",
    "🔁 Repeats",
    "🔍 History", 
    "📊 Analytics",
    "📈 Monthly"
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
                "status": "Pending", "is_repeat": is_repeat, "points": 0, "guest_review": None,
                "sfu_completed": False, "sfu_notes": ""
            })
            st.success(f"✅ Dispatched Order #{new_id} to {assign_to}!")
            st.rerun()

# TAB 2: ACTIVE TASKS (STRICTLY PENDING/IN PROGRESS)
with tab_active:
    st.header("Action Required")
    filter_staff = st.selectbox("View Queue For:", ["All Staff"] + STAFF_LIST, key="active_filter")
    
    filtered_orders = [o for o in db["records"] if (filter_staff == "All Staff" or o.get("assigned_to") == filter_staff) and o.get("status") != "Completed"]
    
    if not filtered_orders:
        st.info("🎉 Current queue cleared.")
    else:
        for order in filtered_orders:
            with st.container():
                st.markdown(f"### Work Order #{order['id']} - Room {order['room']}")
                st.write(f"**Assigned:** {order.get('assigned_to')} | **Type:** {order.get('type')}")
                st.write(f"**Details:** {order.get('desc')}")
                
                if order["status"] == "Pending":
                    if st.button(f"▶️ Start Task #{order['id']}", key=f"s_{order['id']}"):
                        order["status"] = "In Progress"
                        order["started_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        st.rerun()
                        
                elif order["status"] == "In Progress":
                    st.markdown(f"🟢 *Started: {order.get('started_at')}*")
                    comp_note = st.text_input("Resolution Details (Min 4 letters):", key=f"n_{order['id']}")
                    valid = len(comp_note.strip()) >= 4
                    
                    if not valid:
                        st.warning("⚠️ Type at least 4 letters describing your fix to unlock.")
                    
                    if st.button(f"🏁 Complete Task #{order['id']}", key=f"c_{order['id']}", disabled=not valid):
                        order["status"] = "Completed"
                        order["comp_notes"] = comp_note
                        order["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        order["points"] = max(0, 10 - (5 if order.get("is_repeat") else 0))
                        st.success("🏆 Task Closed!")
                        st.rerun()
            st.markdown("---")

# TAB 3: COMPLETED TASKS & QR CODES
with tab_completed:
    st.header("Completed Task Archive")
    
    completed_orders = [o for o in db["records"] if o.get("status") == "Completed"]
    
    if not completed_orders:
        st.info("No tasks completed yet.")
    else:
        for order in reversed(completed_orders[-10:]):
            st.markdown(f"**Order #{order['id']} - Room {order['room']}** | Closed by {order['assigned_to']}")
            st.caption(f"Notes: {order['comp_notes']}")
            st.markdown("---")
            
        with st.expander("📱 Show QR Code for Guest Review"):
            tasks_no_review = [o for o in completed_orders if not o.get("guest_review")]
            if not tasks_no_review:
                st.info("No recent tasks waiting for review.")
            else:
                task_options = {f"Order #{o['id']} - Room {o['room']}": o['id'] for o in tasks_no_review}
                selected_task_label = st.selectbox("Select Task:", list(task_options.keys()))
                
                if selected_task_label:
                    sel_id = task_options[selected_task_label]
                    app_url = "https://12tenbank-collab-building21-app-app-gn893rndmg.streamlit.app"
                    review_url = f"{app_url}?review=true&id={sel_id}"
                    encoded_url = urllib.parse.quote(review_url)
                    qr_api_url = f"https://quickchart.io/qr?text={encoded_url}&size=250"
                    
                    st.info(f"🔗 **Testing Link:** [Tap here to test]({review_url})")
                    col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
                    with col_q2:
                        try:
                            req = urllib.request.Request(qr_api_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req) as response:
                                qr_bytes = response.read()
                            st.image(qr_bytes, use_container_width=True)
                        except Exception as e:
                            st.error("Failed to load QR code.")

# TAB 4: GUEST PORTAL (SFU TRACKING)
with tab_guest:
    st.header("Guest Operations Center")
    st.caption("Central log for all Guest Calls and Supervisor Follow-Ups (SFU).")
    
    guest_orders = [o for o in db["records"] if o.get("type") == "Guest Call"]
    
    if not guest_orders:
        st.success("No guest calls currently logged.")
    else:
        for order in reversed(guest_orders):
            with st.container():
                st.markdown(f"### Order #{order['id']} - Room {order['room']} ({order['status']})")
                st.write(f"**Assigned To:** {order['assigned_to']} | **Dept:** {order['dept']}")
                st.write(f"**Issue:** {order['desc']}")
                
                # SFU Logic Input
                new_sfu = st.checkbox("SFU Completed (Supervisor Follow-Up)", value=order.get("sfu_completed", False), key=f"sfu_check_{order['id']}")
                new_note = st.text_input("Supervisor Notes:", value=order.get("sfu_notes", ""), key=f"sfu_note_{order['id']}")
                
                # Button to commit the SFU update
                if st.button(f"💾 Save SFU Updates (Order #{order['id']})", key=f"sfu_save_{order['id']}"):
                    order["sfu_completed"] = new_sfu
                    order["sfu_notes"] = new_note
                    st.success("Follow-up saved successfully.")
                    st.rerun()
                    
            st.markdown("---")

# TAB 5: REPEAT TASKS
with tab_repeats:
    st.header("Repeat Task Alerts")
    st.caption("Monitoring chronic issues requiring management intervention.")
    
    repeat_orders = [o for o in db["records"] if o.get("is_repeat") == True]
    
    if not repeat_orders:
        st.success("No repeat tasks currently logged! 🎉")
    else:
        for order in repeat_orders:
            st.error(f"🚨 **REPEAT CALL: Room {order['room']}** (Order #{order['id']})")
            st.write(f"Assigned to: {order['assigned_to']} | Status: {order['status']}")
            st.write(f"Issue: {order['desc']}")
            st.markdown("---")

# TAB 6: UNIT HISTORY SEARCH
with tab_history:
    st.header("Unit History & Trends")
    search_room = st.text_input("🔍 Search by Room/Unit Number:")
    if search_room:
        history = [o for o in db["records"] if search_room.lower() in o.get("room", "").lower()]
        if not history:
            st.warning("No previous work orders found.")
        else:
            st.dataframe(pd.DataFrame(history)[["id", "room", "assigned_to", "status", "is_repeat"]], use_container_width=True)

# TAB 7: PERFORMANCE ANALYTICS & HEATMAP
with tab_performance:
    st.header("Team Performance & Building Health")
    
    st.subheader("🏢 Thermal Building Heatmap")
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

# TAB 8: MONTHLY BUILDING PERFORMANCE (GAUGE LAYOUT)
with tab_monthly:
    st.header("Building 21 Monthly Guest Reviews")
    
    df_reviews = db["monthly_reviews"]
    
    # 1. Gauge Section - Big enough to clearly see individual stats
    st.subheader("📊 Performance At A Glance (April 2026)")
    
    # Extract specific data for the current month gauges (April 2026)
    current_month_data = df_reviews[df_reviews['Month'] == 'April 2026'].iloc[0]
    
    gauge_col1, gauge_col2, gauge_col3, gauge_col4 = st.columns(4)
    
    with gauge_col1:
        st.markdown(build_gauge("Overall Rating", current_month_data["Overall Rating"]), unsafe_allow_html=True)
        
    with gauge_col2:
        st.markdown(build_gauge("Overall Satisfaction", current_month_data["Satisfaction"]), unsafe_allow_html=True)
        
    with gauge_col3:
        st.markdown(build_gauge("Cleanliness", current_month_data["Cleanliness"]), unsafe_allow_html=True)
        
    with gauge_col4:
        st.markdown(build_gauge("Staff Rating", current_month_data["Staff"]), unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 2. Raw Data Table with Integrated Input Form
    st.subheader("📄 Official Report Data")
    
    # Data Editor - make placeholder row editable
    updated_reviews = st.data_editor(df_reviews, use_container_width=True, hide_index=True)
    
    # Button to commit the new data
    if st.button("💾 Save Monthly Data to Database"):
        db["monthly_reviews"] = updated_reviews
        st.success("Monthly report data saved successfully.")
        st.rerun()
