import streamlit as st
from streamlit_option_menu import option_menu
import base64
import json
import os
from datetime import datetime
import time

# Simplified app without external dependencies
st.set_page_config(
    page_title="QR Attendance System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 QR Attendance System")
st.info("This is a demo version. Full features require proper deployment setup.")

# Simple navigation
menu = option_menu(
    menu_title="Main Menu",
    options=["Home", "Scanner", "Generator", "Analytics"],
    icons=["house", "camera", "qr-code", "graph-up"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

if menu == "Home":
    st.markdown("""
    ## Welcome to QR Attendance System
    
    This demo shows the basic interface. For full functionality:
    
    1. Clone the repository locally
    2. Install requirements: `pip install -r requirements.txt`
    3. Run: `streamlit run main.py`
    
    GitHub: https://github.com/Belugabilli/Hanish-Singla_Task1
    """)

elif menu == "Scanner":
    st.subheader("📷 QR Scanner")
    st.info("Scanner functionality requires camera access and QR libraries")
    
elif menu == "Generator":
    st.subheader("🔳 QR Generator")
    name = st.text_input("Enter Name:")
    if name and st.button("Generate QR"):
        st.success(f"QR Code for {name} would be generated here")
        
elif menu == "Analytics":
    st.subheader("📊 Analytics Dashboard")
    st.info("Connect to Google Sheets to see live analytics")
