import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import urllib.parse
import time

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
@st.cache_resource
def get_shared_database():
    return {
        "records": [
            {
                "id": 101, "room": "204", "type": "Guest Call", "priority": "Urgent",
                "dept": "Maintenance", "assigned_to": "James W.", "desc": "AC not cooling",
                "created_at": "2026-05-27 08:00:00", "started_at": "2026-05-27 08:05:00",
                "completed_at": "2026-05-27 08:35:00", "comp_notes": "Replaced filter and topped off freon",
                "status": "Completed", "is_repeat": False, "points": 10, "guest_review": None
            }
        ]
    }

db = get_shared_database()
STAFF_LIST = ["James W.", "Stephen S.", "Miguel V.", "Mike R.", "Johanna M.", "Silvia M.", "Dispatch 1"]

# ---------------------------------------------------------
# 3. GUEST REVIEW PORTAL (HIDES MAIN APP IF ACCESSED VIA QR)
# ---------------------------------------------------------
if "review" in st.query_params:
    order_id = int(st.query_params.get("id", 0))
    order = next((o for o in db["records"] if o["id"] == order_id), None)
    
    st.markdown("<h2 style='text-align: center; color: #0A3161;'>Building 21 Guest Feedback</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not order:
        st.error("Invalid review link.")
    elif order.get("guest_review"):
        st.success("✅ Thank you! Your feedback for this service has already been recorded.")
    else:
        st.write(f"**Reviewing Service For:** Room {order['room']}")
        with st.form("guest_review_form"):
            st.markdown("### Rate Your Experience (1 to 5 Stars)")
            quickness = st.slider("1. Quickness / How fast did we respond to your concern?", 1, 5, 5)
            efficiency = st.slider("2. Efficiency / How well did we fix the problem?", 1, 5, 5)
            service = st.slider("3. Customer Service / How friendly and knowledgeable were we?", 1, 5, 5)
            
            st.markdown("### Additional Feedback")
            notes = st.text_area("Any additional notes or comments for our team?")
            contact_mgmt = st.checkbox("I would like to speak with management regarding this service.")
            
            if st.form_submit_button("Submit Review"):
                order["guest_review"] = {
                    "quickness": quickness,
                    "efficiency": efficiency,
                    "service": service,
                    "notes": notes,
                    "contact_mgmt": contact_mgmt,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                st.success("Thank you for your valuable feedback! You may now close this screen.")
                st.rerun()
    st.stop() # This prevents the rest of the staff app from loading for the guest

# ---------------------------------------------------------
# 4. DISPLAY HEADER LOGO (STAFF APP ONLY)
# ---------------------------------------------------------
try:
    col_l1, col_l2, col_l3 = st.columns([1, 4, 1])
    with col_l2:
        logo_img = Image.open("IMG_0783.png")
        st.image(logo_img, use_container_width=True)
except Exception as e:
    pass

st.markdown("<h3 style='text-align: center; color: #0A3161;'>SYNCED WORK ORDER HUB</h3>", unsafe_allow_html=True)
st.markdown("---")

if st.button("🔄 Check For New Dispatches / Updates"):
    st.rerun()

tab_create, tab_active, tab_history, tab_performance = st.tabs([
    "🆕 Create Work Order", 
    "🛠️ Active Tasks & Completion", 
    "🔍 Room History",
    "📊 Analytics"
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
                    "status": "Pending", "is_repeat": is_repeat, "points": 0, "guest_review": None
                }
                db["records"].append(new_order)
                st.success(f"✅ Dispatched Order #{new_id} to {assign_to}!")
                st.rerun()

# TAB 2: ACTIVE TASKS, WORK COMPLETION & QR CODES
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
            
    # NEW FEATURE: QR CODE GENERATOR FOR RECENTLY COMPLETED TASKS
    with st.expander("📱 Show QR Code to Guest for Review (Recently Completed Tasks)"):
        completed_tasks = [o for o in db["records"] if o["status"] == "Completed" and not o.get("guest_review")]
        if not completed_tasks:
            st.info("No recently completed tasks waiting for review.")
        else:
            task_options = {f"Order #{o['id']} - Room {o['room']}": o['id'] for o in completed_tasks}
            selected_task_label = st.selectbox("Select Task to generate QR:", list(task_options.keys()))
            
            if selected_task_label:
                sel_id = task_options[selected_task_label]
                
                app_url = "https://12tenbank-collab-building21-app-app-gn893rndmg.streamlit.app"
                review_url = f"{app_url}?review=true&id={sel_id}"
                encoded_url = urllib.parse.quote(review_url)
                
                # CACHE BUSTER: Forces the API to generate a fresh image
                cache_bust = int(time.time())
                qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_url}&time={cache_bust}"
                
                st.markdown("### Present this code to the guest:")
                st.info(f"🔗 **Testing Link:** [Tap here to test the review page directly]({review_url})")
                
                col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
                with col_q2:
                    st.image(qr_image_url, use_container_width=True)

# TAB 3: UNIT HISTORY SEARCH
with tab_history:
    st.header("Unit History & Trends")
    search_room = st.text_input("🔍 Search by Room/Unit Number (e.g., 21-202A):")
    
    if search_room:
        history = [o for o in db["records"] if search_room.lower() in o["room"].lower()]
        if not history:
            st.warning(f"No previous work orders found for unit '{search_room}'.")
        else:
            st.success(f"Found {len(history)} record(s) for unit '{search_room}'")
            
            df_history = pd.DataFrame(history)
            cols_to_show = ["id", "dept", "assigned_to", "status", "created_at", "comp_notes"]
            st.dataframe(df_history[cols_to_show], use_container_width=True)
            
            st.subheader("Guest Reviews for this Unit")
            reviews = [o for o in history if o.get("guest_review")]
            
            if not reviews:
                st.info("No guest reviews submitted for this unit yet.")
            else:
                for r in reviews:
                    rev = r["guest_review"]
                    st.markdown(f"**Order #{r['id']} ({r['dept']})** | Completed by {r['assigned_to']}")
                    st.write(f"⚡ Quickness: {rev['quickness']}⭐ | 🛠️ Efficiency: {rev['efficiency']}⭐ | 🤝 Service: {rev['service']}⭐")
                    if rev['notes']:
                        st.write(f"🗣️ *\"{rev['notes']}\"*")
                    if rev['contact_mgmt']:
                        st.error("🚨 **GUEST REQUESTED MANAGEMENT CONTACT**")
                    st.markdown("---")

# TAB 4: PERFORMANCE ANALYTICS
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
