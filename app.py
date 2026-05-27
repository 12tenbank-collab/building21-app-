import streamlit as st
import pandas as pd
from datetime import datetime

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
# 2. FREE CENTRAL SYNC DATABASE ENGINE
# ---------------------------------------------------------
# Using Streamlit's global cache as a shared multi-user backplane memory
@st.cache_resource
def get_shared_database():
    # This creates a shared data silo in the cloud server memory accessible by all connected users
    return {
        "records": [
            {
                "id": 101, "room": "204", "type": "Guest Call", "priority": "Urgent",
                "dept": "Maintenance", "assigned_to": "James W.", "desc": "AC not cooling",
                "created_at": "2026-05-27 08:00:00", "started_at": "2026-05-27 08:05:00",
                "completed_at": "2026-05-27 08:35:00", "comp_notes": "Replaced filter and topped off freon",
                "status": "Completed", "is_repeat": False, "points": 10
            }
        ]
    }

db = get_shared_database()
STAFF_LIST = ["James W.", "Stephen S.", "Miguel V.", "Mike R.", "Johanna M.", "Silvia M.", "Dispatch 1"]

# ---------------------------------------------------------
# 3. APPLICATION STRUCTURE
# ---------------------------------------------------------
st.title("BUILDING 21 | SYNCED WORK ORDER HUB")
st.markdown("---")

# Refresh button to manually pull down latest changes from other team members
if st.button("🔄 Check For New Dispatches / Updates"):
    st.rerun()

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
                new_id = max([o["id"] for o in db["records"]]) + 1 if db["records"] else 100
                new_order = {
                    "id": new_id, "room": room, "type": order_type, "priority": priority,
                    "dept": dept, "assigned_to": assign_to, "desc": desc,
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "started_at": "", "completed_at": "", "comp_notes": "",
                    "status": "Pending", "is_repeat": is_repeat, "points": 0
                }
                db["records"].append(new_order)
                st.success(f"✅ Dispatched Order #{new_id} to {assign_to}!")
                st.rerun()

# TAB 2: ACTIVE TASKS & WORK COMPLETION
with tab_active:
    st.header("Staff Execution Hub")
    filter_staff = st.selectbox("View Queue For:", ["All Staff"] + STAFF_LIST)
    
    filtered_orders = [
        o for o in db["records"] 
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
                        st.rerun()
                        
                elif order["status"] == "In Progress":
                    st.markdown(f"🟢 *Started: {order['started_at']}*")
                    comp_note = st.text_input("Resolution Details (Min 4 letters):", key=f"n_{order['id']}")
                    valid = len(comp_note.strip()) >= 4
                    
                    if not valid:
                        st.warning("⚠️ Type at least 4 letters describing your fix to unlock the button.")
                    
                    if st.button(f"🏁 Complete Task #{order['id']}", key=f"c_{order['id']}", disabled=not valid):
                        order["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        order["comp_notes"] = comp_note
                        order["status"] = "Completed"
                        
                        base = 10
                        deductions = 5 if order["is_repeat"] else 0
                        order["points"] = max(0, base - deductions)
                        
                        st.success("🏆 Task Closed out!")
                        st.rerun()
            st.markdown("---")

# TAB 3: PERFORMANCE ANALYTICS
with tab_performance:
    st.header("Team Performance Matrix")
    completed = [o for o in db["records"] if o["status"] == "Completed"]
    if not completed:
        st.info("Performance graphs will populate as tasks shift to completed statuses.")
    else:
        df_perf = pd.DataFrame(completed)
        st.subheader("Efficiency Leaderboard Rankings (Accumulated Points)")
        stats = df_perf.groupby("assigned_to")["points"].sum()
        st.bar_chart(stats, color="#FF7A00")
        st.dataframe(df_perf[["id", "room", "assigned_to", "comp_notes", "points"]], use_container_width=True)
