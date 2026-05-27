import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & CORPORATE BRAND DESIGN THEME
# ---------------------------------------------------------
st.set_page_config(page_title="Building 21 - Work Order Management", layout="wide")

# Updated Design Theme matching the Clean Corporate White, Deep Navy Blue, and Vibrant Orange logo
st.markdown("""
    <style>
    /* Main app background and typography */
    .stApp {
        background-color: #F4F7F9;
        color: #0A3161;
    }
    /* Main Title and Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0A3161 !important;
        font-weight: 700 !important;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #E2E8F0;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #0A3161 !important;
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF7A00 !important;
        color: #FFFFFF !important;
        font-weight: bold;
        border: 1px solid #FF7A00 !important;
    }
    /* Inputs fields border custom accent */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
        border-color: #0A3161 !important;
        color: #0A3161 !important;
    }
    /* Button custom styles */
    div.stButton > button {
        background-color: #0A3161 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #0A3161 !important;
        border-radius: 6px !important;
        padding: 10px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FF7A00 !important;
        color: #FFFFFF !important;
        border: 2px solid #FF7A00 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATABASE CONNECTION (GOOGLE SHEETS)
# ---------------------------------------------------------
try:
    sheet_url = st.secrets["private_sheet_url"]
    csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv&sheet=orders").replace("/edit#gid=", "/gviz/tq?tqx=out:csv&sheet=orders")
except:
    st.error("🔒 Database Link Missing! Please add 'private_sheet_url' to your Streamlit App Secrets.")
    st.stop()

@st.cache_data(ttl=5)
def load_cloud_data():
    try:
        df = pd.read_csv(csv_url)
        df["id"] = df["id"].astype(int)
        df["room"] = df["room"].astype(str)
        df["is_repeat"] = df["is_repeat"].astype(bool)
        df["points"] = df["points"].astype(int)
        return df.to_dict(orient="records")
    except:
        return []

def save_to_cloud(updated_orders):
    st.session_state.master_records = updated_orders

if "master_records" not in st.session_state:
    st.session_state.master_records = load_cloud_data()
else:
    live_pull = load_cloud_data()
    if len(live_pull) > len(st.session_state.master_records):
        st.session_state.master_records = live_pull

orders = st.session_state.master_records
STAFF_LIST = ["James W.", "Stephen S.", "Miguel V.", "Mike R.", "Johanna M.", "Silvia M.", "Dispatch 1"]

# ---------------------------------------------------------
# 3. APPLICATION STRUCTURE (REMOVED "APP" VERBIAGE)
# ---------------------------------------------------------
st.title("BUILDING 21 | SYNCED WORK ORDER HUB")
st.markdown("---")

tab_create, tab_active, tab_performance = st.tabs([
    "🆕 Create Work Order", 
    "🛠️ Active Tasks & Completion", 
    "📊 Performance Analytics"
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
        submit_btn = st.form_submit_button("Dispatch Work Order")
        
        if submit_btn:
            if not room or not desc:
                st.error("❌ Fill out room numbers and task details.")
            else:
                new_id = max([o["id"] for o in orders]) + 1 if orders else 100
                new_order = {
                    "id": new_id, "room": room, "type": order_type, "priority": priority,
                    "dept": dept, "assigned_to": assign_to, "desc": desc,
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "started_at": "", "completed_at": "", "comp_notes": "",
                    "status": "Pending", "is_repeat": is_repeat, "points": 0
                }
                orders.append(new_order)
                save_to_cloud(orders)
                st.success(f"✅ Dispatched Order #{new_id} to {assign_to}!")
                st.rerun()

# TAB 2: ACTIVE TASKS & WORK COMPLETION
with tab_active:
    st.header("Staff Execution Hub")
    filter_staff = st.selectbox("View Queue For:", ["All Staff"] + STAFF_LIST)
    
    filtered_orders = [
        o for o in orders 
        if (filter_staff == "All Staff" or o["assigned_to"] == filter_staff) and o["status"] != "Completed"
    ]
    
    if not filtered_orders:
        st.info("🎉 Current queue cleared.")
    else:
        for idx, order in enumerate(filtered_orders):
            with st.container():
                st.markdown(f"### Work Order #{order['id']} - Room {order['room']} ({order['priority']})")
                st.write(f"**Assigned:** {order['assigned_to']} | **Type:** {order['type']} | **Created:** {order['created_at']}")
                st.write(f"**Notes:** {order['desc']}")
                
                if order["status"] == "Pending":
                    if st.button(f"▶️ Start Task #{order['id']}", key=f"s_{order['id']}"):
                        order["status"] = "In Progress"
                        order["started_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        save_to_cloud(orders)
                        st.rerun()
                        
                elif order["status"] == "In Progress":
                    st.markdown(f"🟢 *Started: {order['started_at']}*")
                    comp_note = st.text_input("Resolution Details (Min 4 letters):", key=f"n_{order['id']}")
                    valid = len(comp_note.strip()) >= 4
                    
                    if st.button(f"🏁 Complete Task #{order['id']}", key=f"c_{order['id']}", disabled=not valid):
                        order["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        order["comp_notes"] = comp_note
                        order["status"] = "Completed"
                        
                        base = 10
                        deductions = 5 if order["is_repeat"] else 0
                        order["points"] = max(0, base - deductions)
                        
                        save_to_cloud(orders)
                        st.success("🏆 Task Closed out!")
                        st.rerun()
            st.markdown("---")

# TAB 3: PERFORMANCE ANALYTICS
with tab_performance:
    st.header("Team Performance Matrix")
    completed = [o for o in orders if o["status"] == "Completed"]
    if not completed:
        st.info("Performance graphs will populate as tasks shift to completed statuses.")
    else:
        df_perf = pd.DataFrame(completed)
        st.subheader("Efficiency Leaderboard Rankings (Accumulated Points)")
        stats = df_perf.groupby("assigned_to")["points"].sum()
        st.bar_chart(stats, color="#FF7A00")
        st.dataframe(df_perf[["id", "room", "assigned_to", "comp_notes", "points"]], use_container_width=True)
