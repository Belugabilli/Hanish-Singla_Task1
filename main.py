import streamlit as st
from streamlit_option_menu import option_menu
import base64
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="QR Attendance System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #D1FAE5;
        border-radius: 0.5rem;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #FEE2E2;
        border-radius: 0.5rem;
        border-left: 5px solid #EF4444;
        margin: 1rem 0;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-radius: 0.5rem;
        border-left: 5px solid #F59E0B;
        margin: 1rem 0;
    }
    .info-message {
        padding: 1rem;
        background-color: #DBEAFE;
        border-radius: 0.5rem;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .scanning-active {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        padding-top: 2rem;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .sidebar-header h1 {
        color: white;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-header p {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
    }
    
    .sidebar-stats {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
    }
    
    .sidebar-stats h3 {
        color: white;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stat-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .stat-label {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
    }
    
    .stat-value {
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .sidebar-footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
    }
    
    .sidebar-footer a {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
    }
    
    .sidebar-footer a:hover {
        color: white;
    }
    
    /* Custom option menu styling */
    div[data-baseweb="menu"] {
        background-color: transparent !important;
    }
    
    .st-cq {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.sheet = None
    st.session_state.attendance_data = None
    st.session_state.current_page = "Home"

st.markdown('<h1 class="main-header">📊 QR Code Attendance System</h1>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h1>📊 QR Attendance</h1>
        <p>Smart Attendance Management System</p>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.8rem; margin-top: 0.5rem;">
            Last Updated: 8 January 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="margin: 1rem 0;">', unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,  
        options=["Home", "Mark Attendance", "Generate QR", "View Analysis"],
        icons=["house-door-fill", "camera-fill", "qr-code-scan", "bar-chart-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "rgba(255, 255, 255, 0.05)",
                "border-radius": "10px",
                "backdrop-filter": "blur(10px)"
            },
            "icon": {
                "color": "white", 
                "font-size": "18px",
                "margin-right": "10px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "padding": "1rem 1.5rem",
                "color": "rgba(255, 255, 255, 0.8)",
                "--hover-color": "rgba(255, 255, 255, 0.15)",
                "border-radius": "8px",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background-color": "rgba(255, 255, 255, 0.2)",
                "color": "white",
                "font-weight": "bold",
                "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.1)"
            },
            "menu-title": {
                "color": "white"
            }
        },
        key="main_navigation"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    st.markdown("""
    <div class="sidebar-stats">
        <h3>📈 Quick Stats</h3>
    """, unsafe_allow_html=True)
    
    try:
        if os.path.exists('encoded_creds.txt'):
            from utils import get_google_sheet
            sheet = get_google_sheet()
            data = sheet.get_all_records()
            
            total = len(data)
            present = len([row for row in data if row.get('Status', '').lower() == 'present'])
            absent = total - present
            scanned_today = len([row for row in data if 
                                row.get('Timestamp', '').split()[0] == datetime.now().strftime('%Y-%m-%d')])
            
            stats = [
                ("Total Participants", f"{total} 👥"),
                ("Present Today", f"{present} ✅"),
                ("Absent Today", f"{absent} ❌"),
                ("Scanned Today", f"{scanned_today} 📅"),
            ]
            
            for label, value in stats:
                st.markdown(f"""
                <div class="stat-item">
                    <span class="stat-label">{label}</span>
                    <span class="stat-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.markdown("""
        <div class="stat-item">
            <span class="stat-label">System Status</span>
            <span class="stat-value">🔧 Setup Required</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0;">
                Connect to Google Sheets to see live stats
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-stats">
        <h3>⚙️ System Status</h3>
        <div class="stat-item">
            <span class="stat-label">QR Scanner</span>
            <span class="stat-value">🟢 Online</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Database Sync</span>
            <span class="stat-value">🟢 Active</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Last Updated</span>
            <span class="stat-value">Just Now</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-stats">
        <h3>⚡ Quick Actions</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", key="sidebar_refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("📤 Export", key="sidebar_export", use_container_width=True):
            st.info("Export feature will be available soon!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-footer">
        <p>v2.1.0 | © 2026 QR Attendance</p>
        <p>Built with ❤️ by Hanish</p>
    </div>
    """, unsafe_allow_html=True)

if selected == "Home":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🎯 Welcome to QR Attendance System
        
        This system allows you to:
        
        ✅ **Mark Attendance** - Scan QR codes to mark participants as present  
        ✅ **Generate QR Codes** - Create unique QR codes for each participant  
        ✅ **View Analysis** - See attendance statistics and reports  
        
        ### 📋 How to Use:
        1. **Generate QR Codes** for participants first
        2. **Scan QR Codes** at event entry
        3. **View real-time attendance** in the Analysis section
        4. **Google Sheet Link :- https://docs.google.com/spreadsheets/d/19tMX_CiRvB0yBjbgt_MJlLg0fY0guQ0vehJQvkSBVo8/edit?usp=sharing**
        
        ### 🔒 Key Features:
        • Duplicate entry prevention
        • Real-time Google Sheets sync
        • QR code generation
        • Attendance analytics
        • Export functionality
        """)

if selected == "Mark Attendance":
    import pages.Mark_Attendance as mark_attendance
    mark_attendance.show()
elif selected == "Generate QR":
    import pages.Generate_QR as generate_qr
    generate_qr.show()
elif selected == "View Analysis":
    import pages.View_Analysis as view_analysis
    view_analysis.show()