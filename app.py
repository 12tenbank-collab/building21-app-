import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & HIGH-CONTRAST ORANGE/BLACK THEME
# ---------------------------------------------------------
st.set_page_config(page_title="Building 21 - Work Order Management", layout="wide")

# Injecting Custom CSS for High-Contrast Black & Orange Theme
st.markdown("""
    <style>
    /* Main app background and text */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #FF5500 !important;
        font-weight: 700 !important;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #111111;
        padding: 10px;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        background-color: #222222;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5500 !important;
        color: #000000 !important;
        font-weight: bold;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #FF5500;
    }
    /* Button custom styles */
    div.stButton > button {
        background-color: #FF5500 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #FF5500 !important;
        border-radius: 5px !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #FFFFFF !important;
    }
    /* Status indicator styling */
    .status-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. STATE MANAGEMENT & SYSTEM CONFIGURATION
# ---------------------------------------------------------
STAFF_LIST = [
    "James W.", 
    "Stephen S.", 
    "Miguel V.", 
    "Mike R.", 
    "Johanna M.", 
    "Silvia M.", 
    "Dispatch 1"
]

# Generate baseline mock data to populate performance charts instantly on first run
if "orders" not in st.session_state:
    now = datetime.now()
    st.session_state.orders = [
        {
            "id": 101, "room": "204", "type": "Guest Call", "priority": "Urgent",
            "dept": "Maintenance", "assigned_to": "James W.", "desc": "AC not cooling",
            "created_at": now - timedelta(days=2), "started_at": now - timedelta(days=2, hours=1),
            "completed_at": now - timedelta(days=2, minutes=30), "comp_notes": "Replaced filter and topped off freon",
            "status": "Completed", "is_repeat": False, "points": 10
        },
        {
            "id": 102, "room": "112", "type": "Supervisor", "priority": "Time Queue",
            "dept": "Housekeeping", "assigned_to": "Silvia M.", "desc": "Deep clean mattress",
            "created_at": now - timedelta(days=1), "started_at": now - timedelta(days=1),
            "completed_at": now - timedelta(days=1, minutes=45), "comp_notes": "Steam cleaned and sanitized",
            "status": "Completed", "is_repeat": False, "points": 10
        },
        {
            "id": 103, "room": "305", "type": "Guest Call", "priority": "Urgent",
            "dept": "Maintenance", "assigned_to": "Miguel V.", "desc": "Leaky faucet",
            "created_at": now - timedelta(hours=5), "started_at": now - timedelta(hours=4, minutes=40),
            "completed_at": now - timedelta(hours=4), "comp_notes": "Replaced O-ring wash gasket",
            "status": "Completed", "is_repeat": True, "points": 5 # Deducted for repeat call
        }
    ]

# ---------------------------------------------------------
# 3. APPLICATION HEADER
# ---------------------------------------------------------
st.title("BUILDING 21 | WORK ORDER & PERFORMANCE SYSTEM")
st.markdown("---")

# Navigation Tabs
tab_create, tab_active, tab_performance = st.tabs([
    "🆕 Create Work Order", 
    "🛠️ Active Tasks & Completion", 
    "📊 Performance Analytics"
])

# ---------------------------------------------------------
# TAB 1: WORK ORDER CREATION
# ---------------------------------------------------------
with tab_create:
    st.header("Log New Work Order")
    
    with st.form("work_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            room = st.text_input("Room Number:", placeholder="e.g. 402, Lobby, Pool")
            order_type = st.selectbox("Type:", ["Supervisor", "Guest Call"])
            priority = st.selectbox("Priority:", ["Urgent", "Time Queue"])
            
        with col2:
            dept = st.selectbox("Department:", ["Housekeeping", "Maintenance"])
            assign_to = st.selectbox("Assign To:", STAFF_LIST)
            is_repeat = st.checkbox("Is this a Repeat Call? (Applies a 5-point performance deduction)")
            
        desc = st.text_area("Request/Work Order Description (Notes Tab):")
        
        submit_btn = st.form_submit_button("Dispatch Work Order")
        
        if submit_btn:
            if not room or not desc:
                st.error("❌ Please provide both a Room Number and a Work Order Description.")
            else:
                new_id = max([o["id"] for o in st.session_state.orders]) + 1 if st.session_state.orders else 100
                new_order = {
                    "id": new_id,
                    "room": room,
                    "type": order_type,
                    "priority": priority,
                    "dept": dept,
                    "assigned_to": assign_to,
                    "desc": desc,
                    "created_at": datetime.now(),
                    "started_at": None,
                    "completed_at": None,
                    "comp_notes": "",
                    "status": "Pending",
                    "is_repeat": is_repeat,
                    "points": 0
                }
                st.session_state.orders.append(new_order)
                st.success(f"✅ Work Order #{new_id} successfully created and assigned to {assign_to}!")

# ---------------------------------------------------------
# TAB 2: ACTIVE TASKS & WORK COMPLETION
# ---------------------------------------------------------
with tab_active:
    st.header("Staff Execution Hub")
    
    # Filter view by employee to reduce noise
    filter_staff = st.selectbox("View Queue For:", ["All Staff"] + STAFF_LIST)
    
    filtered_orders = [
        o for o in st.session_state.orders 
        if (filter_staff == "All Staff" or o["assigned_to"] == filter_staff) and o["status"] != "Completed"
    ]
    
    if not filtered_orders:
        st.info("🎉 No active or pending tasks found for the selection.")
    else:
        for idx, order in enumerate(filtered_orders):
            # Create clear visual boxes for each separate work order
            with st.container():
                st.markdown(f"### Work Order #{order['id']} - Room {order['room']} ({order['priority']})")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f"**Assigned To:** {order['assigned_to']}")
                c2.markdown(f"**Type:** {order['type']}")
                c3.markdown(f"**Dept:** {order['dept']}")
                c4.markdown(f"**Created:** {order['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                st.markdown(f"**Issue Description:** {order['desc']}")
                
                # Handling status progression
                if order["status"] == "Pending":
                    if st.button(f"▶️ Start Task #{order['id']}", key=f"start_{order['id']}_{idx}"):
                        order["status"] = "In Progress"
                        order["started_at"] = datetime.now()
                        st.rerun()
                        
                elif order["status"] == "In Progress":
                    st.markdown(f"🟢 *Task started at: {order['started_at'].strftime('%Y-%m-%d %H:%M:%S')}*")
                    
                    # Target notes field for task resolution
                    comp_note = st.text_input(
                        "Resolution Notes (Minimum 4 characters to unlock completion):", 
                        key=f"note_{order['id']}_{idx}"
                    )
                    
                    # Logic Validation: Check note lengths prior to submission
                    is_valid_length = len(comp_note.strip()) >= 4
                    
                    if not is_valid_length:
                        st.warning("⚠️ Character threshold not met. Type at least 4 characters outlining the resolution steps to enable closure.")
                    
                    # The complete button is only functional/safe to compute if validated
                    if st.button(f"🏁 Complete Task #{order['id']}", key=f"comp_{order['id']}_{idx}", disabled=not is_valid_length):
                        # Capture completion timestamp
                        comp_time = datetime.now()
                        order["completed_at"] = comp_time
                        order["comp_notes"] = comp_note
                        order["status"] = "Completed"
                        
                        # SCORING ENGINE CALCULATION LOGIC
                        base_points = 10
                        deductions = 0
                        
                        # Rule A: Deduct 5 points if flagged as a repeat call
                        if order["is_repeat"]:
                            deductions += 5
                            
                        # Rule B: Deduct 5 points if task sat in queue longer than 15 minutes before being started
                        wait_time = order["started_at"] - order["created_at"]
                        if wait_time > timedelta(minutes=15):
                            deductions += 5
                            
                        final_score = max(0, base_points - deductions)
                        order["points"] = final_score
                        
                        st.success(f"🏆 Task #{order['id']} Closed out! Points Awarded: {final_score}")
                        st.rerun()
            st.markdown("---")

# ---------------------------------------------------------
# TAB 3: PERFORMANCE ANALYTICS (GAMIFICATION ENGINE)
# ---------------------------------------------------------
with tab_performance:
    st.header("Team Performance Matrix")
    
    completed_orders = [o for o in st.session_state.orders if o["status"] == "Completed"]
    
    if not completed_orders:
        st.info("No tasks completed yet. Performance analytics will populate dynamically once metrics are logged.")
    else:
        df = pd.DataFrame(completed_orders)
        
        # Ensure proper time series handling
        now = datetime.now()
        df["completed_at"] = pd.to_datetime(df["completed_at"])
        
        # Filter groups for performance scopes
        df_daily = df[df["completed_at"] >= (now - timedelta(days=1))]
        df_weekly = df[df["completed_at"] >= (now - timedelta(days=7))]
        df_monthly = df[df["completed_at"] >= (now - timedelta(days=30))]
        
        # Metric Layouts
        g_col1, g_col2, g_col3 = st.columns(3)
        
        with g_col1:
            st.subheader("📆 Daily Efficiency Rank")
            if not df_daily.empty:
                daily_stats = df_daily.groupby("assigned_to")["points"].sum()
                st.bar_chart(daily_stats, color="#FF5500")
            else:
                st.write("No metrics compiled for today yet.")
                
        with g_col2:
            st.subheader("🗓️ Weekly Efficiency Rank")
            if not df_weekly.empty:
                weekly_stats = df_weekly.groupby("assigned_to")["points"].sum()
                st.bar_chart(weekly_stats, color="#FFAA00")
            else:
                st.write("No metrics compiled for this week yet.")
                
        with g_col3:
            st.subheader("🗃️ Monthly Efficiency Rank")
            if not df_monthly.empty:
                monthly_stats = df_monthly.groupby("assigned_to")["points"].sum()
                st.bar_chart(monthly_stats, color="#FF3300")
            else:
                st.write("No metrics compiled for this month yet.")
                
        # Historic Audit Log Data Table
        st.markdown("### Historical Resolution Audit Logs")
        display_df = df[[
            "id", "room", "assigned_to", "type", "priority", 
            "created_at", "started_at", "completed_at", "comp_notes", "points"
        ]].copy()
        
        # Format timestamps cleanly for human eyes
        for col in ["created_at", "started_at", "completed_at"]:
            display_df[col] = display_df[col].dt.strftime('%m/%d %H:%M')
            
        st.dataframe(display_df.sort_values(by="id", ascending=False), use_container_width=True)
