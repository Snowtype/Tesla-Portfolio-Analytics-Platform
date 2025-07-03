import streamlit as st
# Modify page width and navigation bar expansion settings
# [IMPORTANT] set_page_config must be the first Streamlit command, so placed at the top
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

import pandas as pd
import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
from pathlib import Path

from page_modules import (
    user_segment_mau, 
    new_subscribers, 
    region_age_data, 
    repurchase_rate, 
    heavy_users_by_menu, 
    heavy_users_simple, 
    sales_by_category,
    non_new_sig_customers,
    regional_purchase_analysis,
    hourly_regional_product_sales  # Added new page
)

# Brand configuration import
from brand_config import BRAND_SCHEMA, get_brand_texts, PORTFOLIO_USERS

# ------------------------
# [Security utility import]
# ------------------------
try:
    from security_utils import SecurityUtils, log_security_event
except ImportError:
    # Define default functions if security_utils is not available
    class SecurityUtils:
        @staticmethod
        def log_login_attempt(username, success, ip_address=None):
            pass
    
    def log_security_event(event_type, user, details, ip_address=None):
        pass

# ------------------------
# [IP address tracking function]
# ------------------------
def get_client_ip():
    """Track client IP address"""
    try:
        # Track IP using Streamlit's built-in features
        if hasattr(st, 'get_option') and st.get_option('server.address') != 'localhost':
            # In actual server environment, client IP can be tracked
            return "unknown"  # In real implementation, extract IP from proxy headers
        else:
            # Provide more specific information in local development environment
            import socket
            try:
                # Get local IP address
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return f"local-{local_ip}"
            except:
                # Use hostname if failed
                try:
                    hostname = socket.gethostname()
                    return f"local-{hostname}"
                except:
                    return "localhost-dev"
    except:
        return "localhost-dev"

# ------------------------
# [Brand-specific schema management] - Only schema differs by brand, DB/table structure is the same
# ------------------------
BRAND_SCHEMA = {
    "BRAND_A": "ANALYSIS_BRAND_A",  # Coffee Brand A
    "BRAND_B": "ANALYSIS_BRAND_B",  # Coffee Brand B
}

# ------------------------
# [Account/Brand/Permission information management] - Includes brand and role information by account
# ------------------------
USERS = {
    "brand_a_user": {"password": "[MASKED]", "brand": "BRAND_A", "role": "user"},
    "brand_b_user": {"password": "[MASKED]", "brand": "BRAND_B", "role": "user"},
    "admin": {"password": "[MASKED]", "brand": "BRAND_A", "role": "admin"},
}

# ------------------------
# [Session save/restore functionality] - File-based session management
# ------------------------
def save_session_to_file(session_data):
    """Save session data to file"""
    session_file = Path(".streamlit/session.json")
    session_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Session save failed: {e}")
        return False

def load_session_from_file():
    """Load session data from file"""
    session_file = Path(".streamlit/session.json")
    
    if not session_file.exists():
        return None
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Validate session data (check if within 24 hours)
        if "login_timestamp" in session_data:
            login_time = pd.Timestamp(session_data["login_timestamp"])
            current_time = pd.Timestamp.now()
            if (current_time - login_time).total_seconds() > 24 * 3600:
                # Delete session file if over 24 hours
                session_file.unlink()
                return None
        
        return session_data
    except Exception as e:
        st.error(f"Session load failed: {e}")
        return None

def clear_session_file():
    """Delete session file"""
    session_file = Path(".streamlit/session.json")
    if session_file.exists():
        try:
            session_file.unlink()
        except Exception as e:
            st.error(f"Session file deletion failed: {e}")

# ------------------------
# [Login functionality] - Save brand/permission information to session upon successful login
# ------------------------
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    
    if login_btn:
        # Track IP address
        client_ip = get_client_ip()
        
        if username in USERS and USERS[username]["password"] == password:
            # Log successful login
            SecurityUtils.log_login_attempt(username, True, client_ip)
            
            # Set session state
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["brand"] = USERS[username]["brand"]
            st.session_state["role"] = USERS[username]["role"]
            st.session_state["login_timestamp"] = pd.Timestamp.now().isoformat()
            st.session_state["client_ip"] = client_ip
            
            # Save session data to file
            session_data = {
                "logged_in": True,
                "username": username,
                "brand": USERS[username]["brand"],
                "role": USERS[username]["role"],
                "login_timestamp": st.session_state["login_timestamp"],
                "client_ip": client_ip
            }
            save_session_to_file(session_data)
            
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            # Log failed login
            SecurityUtils.log_login_attempt(username, False, client_ip)
            st.error("Incorrect username or password.")

# Check and restore login status
def check_login_status():
    # First check login information in session state
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        # Check login time (verify if within 24 hours)
        if "login_timestamp" in st.session_state:
            login_time = pd.Timestamp(st.session_state["login_timestamp"])
            current_time = pd.Timestamp.now()
            # Keep login if within 24 hours
            if (current_time - login_time).total_seconds() < 24 * 3600:
                return True
            else:
                # Logout if over 24 hours
                st.session_state["logged_in"] = False
                st.session_state["username"] = ""
                st.session_state["brand"] = ""
                st.session_state["role"] = ""
                clear_session_file()
                return False
    
    # If no session state login info, try to restore from file
    session_data = load_session_from_file()
    if session_data and session_data.get("logged_in"):
        # Restore session state
        st.session_state["logged_in"] = True
        st.session_state["username"] = session_data.get("username", "")
        st.session_state["brand"] = session_data.get("brand", "")
        st.session_state["role"] = session_data.get("role", "")
        st.session_state["login_timestamp"] = session_data.get("login_timestamp", "")
        st.session_state["client_ip"] = session_data.get("client_ip", "")
        return True
    
    return False

# If login status is not logged in, show login page
if not check_login_status():
    login()
    st.stop()
    
# Logout button
with st.sidebar:
    username = st.session_state.get('username', 'N/A')
    brand = st.session_state.get('brand', 'N/A')
    role = st.session_state.get('role', 'N/A')
    st.markdown(f"**Login account:** {username} (Brand: {brand}, Role: {role})")
    if st.button("Logout"):
        # Reset session state
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["brand"] = ""
        st.session_state["role"] = ""
        if "login_timestamp" in st.session_state:
            del st.session_state["login_timestamp"]
        
        # Delete session file
        clear_session_file()
        
        st.rerun()

# ------------------------
# [Admin page branching] - Only admin account can access
# ------------------------
def admin_page():
    st.title("🔐 Admin Page")
    st.markdown("### Security Management and System Monitoring")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "🔒 Security Logs", "📊 System Status", "⚙️ Settings"])
    
    with tab1:
        st.header("User Management")
        
        # Display current user list
        st.subheader("Current Registered Users")
        user_data = []
        for user, info in USERS.items():
            user_data.append({
                "Username": user,
                "Brand": info['brand'],
                "Role": info['role'],
                "Status": "Active"
            })
        
        df_users = pd.DataFrame(user_data)
        st.dataframe(df_users, use_container_width=True)
        
        # Role change functionality (simulation)
        st.subheader("Role Change")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_user = st.selectbox("Target User", list(USERS.keys()))
        
        with col2:
            new_role = st.selectbox("New Role", ["user", "admin", "manager"])
        
        with col3:
            if st.button("Role Change"):
                if target_user and new_role:
                    old_role = USERS[target_user]["role"]
                    # Actual DB update
                    USERS[target_user]["role"] = new_role
                    
                    # Log role change
                    SecurityUtils.log_permission_change(
                        admin_user=st.session_state.get("username", "unknown"),
                        target_user=target_user,
                        old_role=old_role,
                        new_role=new_role
                    )
                    
                    st.success(f"Role for {target_user} changed from {old_role} to {new_role}")
    
    with tab2:
        st.header("Security Log View")
        
        # List of log files by port
        st.subheader("Log Files by Port")
        log_files = []
        for port in [8501, 8502, 8503, 8504]:
            log_file = f"security_events_port_{port}.log"
            if Path(log_file).exists():
                log_files.append((port, log_file))
        
        # Also check default log file
        if Path("security_events.log").exists():
            log_files.append(("default", "security_events.log"))
        
        if log_files:
            # Select port
            selected_port = st.selectbox(
                "Select Port", 
                [f"Port {port}" for port, _ in log_files],
                index=0
            )
            
            # Selected port's log file path
            selected_log_file = log_files[log_files.index(selected_port)][1]
            
            # Read log file
            try:
                with open(selected_log_file, "r", encoding="utf-8") as f:
                    log_lines = f.readlines()
                
                if log_lines:
                    st.subheader(f"Recent Security Events ({selected_log_file})")
                    
                    # Display recent 20 logs
                    recent_logs = log_lines[-20:]
                    
                    for log_line in recent_logs:
                        try:
                            log_data = json.loads(log_line.strip())
                            with st.expander(f"{log_data['timestamp']} - {log_data['event_type']} - {log_data['user']} (IP: {log_data.get('ip_address', 'N/A')})"):
                                st.json(log_data)
                        except:
                            st.text(log_line.strip())
                else:
                    st.info(f"No logs found in {selected_log_file}")
                    
            except FileNotFoundError:
                st.info(f"Could not find {selected_log_file}")
        else:
            st.info("No security log files found yet")
        
        # Log filtering
        st.subheader("Log Filtering")
        event_types = ["LOGIN_SUCCESS", "LOGIN_FAILED", "DATA_ACCESS", "PERMISSION_CHANGE"]
        selected_event = st.selectbox("Select Event Type", ["All"] + event_types)
        
        if st.button("Refresh Logs"):
            st.rerun()
    
    with tab3:
        st.header("System Status")
        
        # Current session information
        st.subheader("Current Session Information")
        session_info = {
            "User": st.session_state.get("username", "N/A"),
            "Brand": st.session_state.get("brand", "N/A"),
            "Role": st.session_state.get("role", "N/A"),
            "Login Time": st.session_state.get("login_timestamp", "N/A"),
            "IP Address": st.session_state.get("client_ip", "N/A")
        }
        
        for key, value in session_info.items():
            st.write(f"**{key}:** {value}")
        
        # System metrics
        st.subheader("System Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Users", len(USERS))
        
        with col2:
            st.metric("Total Brands", len(set(info['brand'] for info in USERS.values())))
        
        with col3:
            st.metric("Admin Count", len([u for u, info in USERS.items() if info['role'] == 'admin']))
    
    with tab4:
        st.header("Security Settings")
        
        st.subheader("Session Management")
        if st.button("Force Logout All Sessions"):
            # In reality, this would invalidate all sessions in DB
            st.success("All user sessions have been force logged out.")
            SecurityUtils.log_security_event(
                "FORCE_LOGOUT_ALL",
                st.session_state.get("username", "unknown"),
                {"action": "Force logout all sessions"}
            )
        
        st.subheader("Log Management")
        if st.button("Backup Security Logs"):
            st.info("Security log backup functionality would be implemented to save to file system or DB.")
        
        if st.button("Clean Old Logs"):
            st.info("Cleaning logs older than 30 days.")
            SecurityUtils.log_security_event(
                "LOG_CLEANUP",
                st.session_state.get("username", "unknown"),
                {"action": "Clean old logs"}
            )

# ------------------------
# [Snowflake connection and session management]
# ------------------------
# For portfolio demonstration, we'll use a simple mock connection
try:
    from snowflake_connection import get_session
    session = get_session()
except ImportError:
    # Use simple mock session for portfolio
    class MockSession:
        def sql(self, query):
            # Return empty DataFrame for demonstration
            return pd.DataFrame()
    session = MockSession()

# Header image
def get_header_image(brand):
    header_images = {
        "BRAND_A": "https://via.placeholder.com/1200x200/FF6B6B/FFFFFF?text=Coffee+Brand+A+Analytics",
        "BRAND_B": "https://via.placeholder.com/1200x200/4ECDC4/FFFFFF?text=Coffee+Brand+B+Analytics"
    }
    # Default is BRAND_A
    brand = brand or "BRAND_A"
    url = header_images.get(brand, header_images["BRAND_A"])
    
    try:
        st.image(url, use_container_width=True)
    except:
        st.info(f"Analytics Dashboard - {get_brand_texts(brand)['title']}")

# Footer image
def display_footer_image():
    url = """https://ifh.cc/g/1pTNdZ.jpg"""
    st.image(url, use_container_width=True)

# ------------------------
# 1. Session state initialization
# ------------------------
if "page" not in st.session_state:
    st.session_state.page = "User Segment and MAU"

# ------------------------
# 2. Page definitions (dictionary)
# ------------------------
pages = {
    "User Segment and MAU": {
        "description": "This page analyzes inactive customer segments. You can check key user metrics and behavioral patterns.",
        "details": [
            "Data: In-app customer activity logs + purchase history",
            {"Visualization Panel": ["Coffee Brand A registered users and inactive users", "MAU bar chart", "User segment status (color-coded)"]},
        ]
    },
    "Daily New Subscribers": {
        "description": "Examine daily new subscriber trends and conduct trend analysis.",
        "details": [
            "Data: Daily new subscriber count",
            {"Visualization Panel": ["New subscriber trend graph", "Weekly/monthly comparison chart"]},
            "Additional Analysis: Analysis of subscriber increase factors"
        ]
    },
    "Regional/Age Data": {
        "description": "Analyze customer regional and age data to derive insights.",
        "details": [
            "Data: Regional user distribution, age group user statistics",
            {"Visualization Panel": ["Regional heatmap", "Age group pie chart"]},
            "Additional Analysis: Regional and age group purchase pattern analysis"
        ]
    },
    "Heavy User Segmentation by Menu": {
        "description": "Segment heavy users by menu to conduct in-depth analysis of user behavior.",
        "details": [
            "Data: Menu usage frequency, user behavior logs",
            {"Visualization Panel": ["User distribution graph by menu", "Heavy user behavior pattern chart"]},
            "Additional Analysis: Heavy user retention strategy analysis"
        ]
    },
    "Heavy User Analysis": {
        "description": "Analyze heavy user data in a stable and clean manner.",
        "details": [
            "Data: Heavy user order analysis",
            {"Visualization Panel": ["Order analysis by gender/age group", "Order frequency by menu", "Order patterns by day of week"]},
            "Additional Analysis: Filtering and data download"
        ]
    },
    "Sales by Category": {
        "description": "Analyze sales by each category and evaluate performance.",
        "details": [
            "Data: Sales data by category",
            {"Visualization Panel": ["Sales chart by category", "Sales ratio by subcategory", "Growth rate line chart"]},
            "Additional Analysis: Revenue enhancement strategy proposals"
        ]
    },
    "Repurchase Customer Rate": {
        "description": "Summarize repurchase user data to provide key metrics and statistics.",
        "details": [
            "Data: User count data by order frequency",
            {"Visualization Panel": ["Bar graph"]},
            "Additional Analysis: Complete data download"
        ]
    },
    "Non-New/Signature Purchase Customers": {
        "description": "Analyze customers who purchased beverages within the last 30 days but did not purchase new/signature products.",
        "details": [
            "Data: Non-new/signature purchase customer data (DT_BRAND_A_NON_NEW_SIG_CUSTOMERS)",
            {"Visualization Panel": ["Total target customer count", "Daily customer count trend", "Weekly customer count aggregation"]},
            "Additional Analysis: Customer list download, marketing utilization ideas"
        ]
    },
    "Regional Purchase Cycle and Key Products": {
        "description": "Analyze regional purchase cycles and popular products to establish regional customized marketing strategies.",
        "details": [
            "Data: Regional purchase cycles (DT_BRAND_A_PURCHASE_INTERVAL_BY_REGION), Regional popular products (DT_BRAND_A_TOP_PRODUCTS_BY_REGION)",
            {"Visualization Panel": ["Regional average purchase cycle comparison", "Regional TOP 5 popular products", "Product diversity analysis"]},
            "Additional Analysis: Regional marketing strategy proposals, data download"
        ]
    },
    "Regional Hourly Product Sales Trends": {
        "description": "Analyze regional hourly product sales patterns to establish time-based operational optimization strategies.",
        "details": [
            "Data: Hourly regional product sales data (DT_BRAND_A_HOURLY_PRODUCT_SALES_BY_REGION)",
            {"Visualization Panel": ["Hourly TOP 5 popular products", "Product sales trends by time", "Regional time heatmap"]},
            "Additional Analysis: Peak time analysis, operational optimization insights, data download"
        ]
    }
}
if st.session_state["role"] == "admin":
    pages["Admin Page"] = {"description": "Provides admin functions including account/brand management, log checking", "details": []}

# ------------------------
# 3. Sidebar styling and INDEX display (first display)
# ------------------------
# Current page according to dynamic styling generation
current_page = st.session_state.page

st.sidebar.markdown(f"""
    <style>
    /* Sidebar default style */
    [data-testid="stSidebar"] {{ 
        background: #F0F0F0; 
        padding: 20px; 
    }}
    [data-testid="stSidebarCloseButton"] {{ display: none; }}
    
    /* Text style */
    .header-text {{ font-size: 24px; font-weight: bold; text-align: left; margin-bottom: 1px; }}
    .report-text {{ font-size: 20px; font-weight: bold; margin-top: 20px; text-align: right; }}
    .sub-text {{ font-size: 14px; text-align: right; color: #333333; margin-bottom: 10px; }}
    .index {{ font-size: 20px; text-align: left; color: #333333; margin-top: 30px; margin-bottom: 15px; font-weight: bold; }}
    
    /* Button style */
    .stButton > button {{ 
        width: 100%; 
        margin: 5px 0; 
        font-size: 16px; 
        padding: 10px; 
        color: white; 
        background-color: #7E7E7E; 
        border: none; 
        border-radius: 5px; 
    }}
    .stButton > button:hover {{ 
        background-color: #f9e2b6; 
        color: #d39824;
    }}
    .stButton > button:active {{ 
        background-color: #f9e2b6; 
        color: #d39824; 
    }}
    .stButton > button:focus {{ 
        color: #8e6c2b !important; 
        outline: #8e6c2b; 
    }}
    </style>
    
    <script>
    // Current page button color forced setting
    function setCurrentPageButton() {{
        const buttons = document.querySelectorAll('.stButton button');
        const currentPage = '{current_page}';
        
        buttons.forEach(button => {{
            if (button.textContent.trim() === currentPage) {{
                button.style.backgroundColor = '#000';
                button.style.color = '#FF6060';
            }} else {{
                button.style.backgroundColor = '#7E7E7E';
                button.style.color = 'white';
            }}
        }});
    }}
    
    // Page load execution
    setCurrentPageButton();
    
    // Periodic execution (main screen click response)
    setInterval(setCurrentPageButton, 100);
    </script>
    """, unsafe_allow_html=True)

# 4. Sidebar top place to show current page details
current_page_placeholder = st.sidebar.empty()
# Sidebar period selection date MAU user segment
top_placeholder = st.sidebar.empty()

# 6. Nested list item assembly
list_items = []
for detail in pages[st.session_state.page]['details']:
    if isinstance(detail, str):
        list_items.append(f"<li>{detail}</li>")
    elif isinstance(detail, dict):
        key = list(detail.keys())[0]
        sub_details = detail[key]
        sub_list = ''.join([f"<li>{sd}</li>" for sd in sub_details])
        list_items.append(f"<li><strong>{key}</strong>:<ul>{sub_list}</ul></li>")
html_list = ''.join(list_items)

# 7. Sidebar top "Current Page" and details display
html_code = f"""
<div style="margin-top: 20px;">
  <div style="font-size:24px; font-weight:bold; color:#B8865B; margin-top:4px;">
    {st.session_state.page}
  </div>
  <div style="font-size:14px; color:#555; margin-top:10px;">
    {pages[st.session_state.page]['description']}
    <ul>
      {html_list}
    </ul>
  </div>
  <div style="height:25px;"></div>
</div>
"""
current_page_placeholder.markdown(html_code, unsafe_allow_html=True)

# 8. Sidebar page selection buttons (first display)
def set_page(page):
    st.session_state.page = page

for page in pages.keys():
    # Check if current page
    is_current_page = (page == current_page)
    
    # Special key for current page button
    button_key = f"current_page_{page}" if is_current_page else f"page_{page}"
    
    st.sidebar.button(page, key=button_key, on_click=set_page, args=(page,))

# ------------------------
# 9. Main page content (later display)
# ------------------------
month_options = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
}

get_header_image(st.session_state["brand"])

# Inactive customer segment
if st.session_state.page == "User Segment and MAU":
    user_segment_mau.show_page(session, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

# Daily new subscribers
elif st.session_state.page == "Daily New Subscribers":
    new_subscribers.show_page(session, top_placeholder, month_options, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Regional/Age Data":
    region_age_data.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Heavy User Segmentation by Menu":
    heavy_users_by_menu.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Heavy User Analysis":
    heavy_users_simple.show_page(session, top_placeholder, month_options, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Sales by Category":
    sales_by_category.show_page(session, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Repurchase Customer Rate":
    repurchase_rate.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Non-New/Signature Purchase Customers":
    non_new_sig_customers.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Regional Purchase Cycle and Key Products":
    regional_purchase_analysis.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Regional Hourly Product Sales Trends":
    hourly_regional_product_sales.show_page(session, top_placeholder, brand=st.session_state["brand"], schema=BRAND_SCHEMA.get(st.session_state["brand"], "ANALYSIS_BRAND_A"), role=st.session_state["role"])

elif st.session_state.page == "Admin Page":
    if st.session_state["role"] == "admin":
        admin_page()
    else:
        st.error("Access denied.")
    st.stop()
        
# Footer image display
display_footer_image()

# Sidebar feature overview
def show_sidebar_info():
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 **Analysis Features**")
        
        features = [
            {"📈 User Analysis": ["MAU User Status", "Segment Analysis", "Subscriber Trend"]},
            {"🎯 Marketing Analysis": ["New Subscriber Trend", "Regional Age Analysis", "Repurchase Rate Analysis"]},
            {"💰 Sales Analysis": ["Sales by Category", "Regional Sales Pattern", "Hourly Sales"]},
            {"👥 Customer Behavior": ["Heavy User Analysis", "Menu Purchase Pattern", "Regional Preference"]},
            {"📋 Operation Indicators": ["Daily/Monthly Trend", "Customer Segment Status", "Business KPI"]}
        ]
        
        for feature_group in features:
            for title, items in feature_group.items():
                st.markdown(f"**{title}**")
                for item in items:
                    st.markdown(f"  • {item}")
        
        st.markdown("---")
        st.markdown("### 🔍 **Data Source**")
        st.markdown("""
        **Main Tables**:
        - User Data (DT_BRAND_A_USER_COUNTS)
        - MAU Data (DT_BRAND_A_MAU_USERS) 
        - Sales Data (DT_BRAND_A_SALES_*)
        - Regional Analysis (DT_BRAND_A_REGION_*)
        
        > 💡 **Portfolio Note**: Actual table names and data are masked for privacy.
        """) 