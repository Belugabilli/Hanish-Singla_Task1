import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import time
from datetime import datetime
from utils import get_google_sheet, mark_attendance
import os
import warnings


warnings.filterwarnings('ignore')
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'

def show():
    st.markdown('<h1 class="main-header">📷 Mark Attendance - QR Scanner</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'scanning' not in st.session_state:
        st.session_state.scanning = False
    if 'last_scanned' not in st.session_state:
        st.session_state.last_scanned = None
    if 'scanned_codes' not in st.session_state:
        st.session_state.scanned_codes = set()
    if 'camera_index' not in st.session_state:
        st.session_state.camera_index = 0
    if 'marked_records' not in st.session_state:
        st.session_state.marked_records = []

    def get_available_cameras():
        """Get list of available cameras without triggering errors"""
        available_cameras = []
        
        # Try common camera indexes
        for i in range(3):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(f"Camera {i}")
                    cap.release()
            except:
                continue
        
        return available_cameras

    def scan_qr_code(camera_index=0):
        """Function to scan QR codes from webcam with error handling"""
        try:
            backends = [
                cv2.CAP_DSHOW,  
                cv2.CAP_MSMF,   
                cv2.CAP_ANY     
            ]
            
            cap = None
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(camera_index, backend)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        break
                except:
                    if cap:
                        cap.release()
                    continue
            
            if cap is None or not cap.isOpened():
                st.error("❌ Could not access camera. Please check your camera connection.")
                st.session_state.scanning = False
                return
            
            stframe = st.empty()
            stop_placeholder = st.empty()
            
            if stop_placeholder.button("🛑 Stop Scanning", key="stop_scanner"):
                st.session_state.scanning = False
            
            last_scan_time = time.time()
            scan_cooldown = 2  
            
            while st.session_state.scanning:
                ret, frame = cap.read()
                if not ret:
                    st.warning("Camera frame not available. Trying again...")
                    time.sleep(0.5)
                    continue
                
                frame = cv2.resize(frame, (640, 480))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                try:
                    # Decode QR codes
                    decoded_objects = decode(gray)
                    
                    for obj in decoded_objects:
                        data = obj.data.decode('utf-8').strip()
                        
                        current_time = time.time()
                        if current_time - last_scan_time < scan_cooldown:
                            continue
                        
                        points = obj.polygon
                        if len(points) == 4:
                            pts = np.array(points, dtype=np.int32)
                            pts = pts.reshape((-1, 1, 2))
                            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                        
                        cv2.putText(frame, f"QR: {data[:20]}...", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.7, (0, 0, 255), 2)
                        
                        if data and data != st.session_state.last_scanned:
                            process_qr_data(data)
                            st.session_state.last_scanned = data
                            last_scan_time = current_time
                    
                except Exception as e:
                    pass

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(rgb_frame, channels="RGB", use_column_width=True)
                
                if not st.session_state.scanning:
                    break
                
                time.sleep(0.05)
            
            # Release camera
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            st.error(f"Camera error: {str(e)}")
            st.session_state.scanning = False

    def process_qr_data(qr_data):
        """Process scanned QR data"""
        try:
            if '_' in qr_data:
                parts = qr_data.split('_')
                reg_num = parts[0]
                name = '_'.join(parts[1:]) if len(parts) > 1 else "Unknown"
            else:
                reg_num = qr_data.strip()
                name = "Unknown"
            
            if not reg_num:
                st.warning("⚠️ Invalid QR code: No registration number found")
                return
            
            if reg_num in st.session_state.scanned_codes:
                st.warning(f"⚠️ {name} ({reg_num}) already marked in this session!")
                return
            
            worksheet = get_google_sheet()
            
            # Mark attendance
            result, participant_name = mark_attendance(worksheet, reg_num)
            
            if result == "marked":
                st.session_state.scanned_codes.add(reg_num)
                display_name = participant_name if participant_name else name
                
                # Add to marked records
                st.session_state.marked_records.append({
                    'name': display_name,
                    'reg_num': reg_num,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'status': 'Newly Marked'
                })
                
                # Success message
                success_placeholder = st.empty()
                success_placeholder.markdown(f"""
                <div class="success-message">
                <h3>🎉 Attendance Marked Successfully!</h3>
                <p><strong>Name:</strong> {display_name}</p>
                <p><strong>Registration:</strong> {reg_num}</p>
                <p><strong>Status:</strong> ✅ PRESENT</p>
                <p><strong>Time:</strong> {datetime.now().strftime("%H:%M:%S")}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.balloons()
                
                time.sleep(3)
                success_placeholder.empty()
                
            elif result == "already_present":
                display_name = participant_name if participant_name else name
                
                # Warning message for already marked
                warning_placeholder = st.empty()
                warning_placeholder.markdown(f"""
                <div class="warning-message">
                <h3>⚠️ Already Marked Present!</h3>
                <p><strong>Name:</strong> {display_name}</p>
                <p><strong>Registration:</strong> {reg_num}</p>
                <p><strong>Status:</strong> ✅ ALREADY PRESENT</p>
                <p><strong>Time:</strong> {datetime.now().strftime("%H:%M:%S")}</p>
                <p><em>This participant was already marked as present earlier.</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add to marked records as already present
                st.session_state.marked_records.append({
                    'name': display_name,
                    'reg_num': reg_num,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'status': 'Already Present'
                })
                
                time.sleep(3)
                warning_placeholder.empty()
                
            else:
                st.markdown(f"""
                <div class="error-message">
                <h3>❌ Registration Not Found</h3>
                <p>Registration number <strong>{reg_num}</strong> not found in database.</p>
                <p>Please generate QR code first or check the registration number.</p>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.markdown(f"""
            <div class="error-message">
            <h3>❌ Error Processing QR Code</h3>
            <p>Error: {str(e)}</p>
            </div>
            """, unsafe_allow_html=True)

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### 📋 Instructions:
        
        1. **Select your camera** from the dropdown below
        2. Click **📷 Start Scanner** to activate camera
        3. Show **QR code** to camera (hold steady)
        4. Wait for confirmation message
        5. Click **🛑 Stop Scanner** when done
        
        ---
        ### 💡 Tips:
        • Ensure good lighting
        • Hold QR code steady in frame
        • Keep QR code parallel to camera
        • If scanner doesn't work, use manual entry
        """)
        

        st.markdown("### 🔍 Camera Selection")
        
        available_cameras = get_available_cameras()
        
        if available_cameras:
            selected_camera = st.selectbox(
                "Choose camera:",
                available_cameras,
                index=0,
                help="Select the camera you want to use for scanning"
            )
            st.session_state.camera_index = int(selected_camera.split()[-1])
            st.success(f"✅ Camera {st.session_state.camera_index} selected and ready!")
        else:
            st.warning("⚠️ No cameras detected! Using default camera.")
            st.session_state.camera_index = 0

    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("📷 Start Scanner", 
                        key="start",
                        use_container_width=True,
                        help="Start QR code scanning"):
                st.session_state.scanning = True
                st.rerun()
        
        with action_col2:
            if st.button("🛑 Stop Scanner", 
                        key="stop",
                        use_container_width=True,
                        help="Stop QR code scanning"):
                st.session_state.scanning = False
                st.rerun()
        
        if st.button("🔄 Clear Session", 
                    key="clear",
                    use_container_width=True,
                    help="Clear current scanning session"):
            st.session_state.scanning = False
            st.session_state.scanned_codes.clear()
            st.session_state.last_scanned = None
            st.session_state.marked_records = []
            st.success("Session cleared! Ready for new scanning.")
            st.rerun()

    # Scanner section
    if st.session_state.scanning:
        st.markdown("---")
        st.markdown("### 🎥 Live Scanner Active")
        st.markdown('<p class="scanning-active">🔴 Camera is ON - Show QR code to camera</p>', unsafe_allow_html=True)
        
        # Start scanning
        scan_qr_code(st.session_state.camera_index)
        
        if not st.session_state.scanning:
            st.success("✅ Scanner stopped successfully")
    else:
        st.info("👆 Click **'Start Scanner'** to begin scanning QR codes")


    st.markdown("---")
    st.markdown("### 🖋️ Manual Entry (Alternative)")

    with st.expander("Click here for manual entry", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            manual_reg = st.text_input(
                "Enter Registration Number:",
                placeholder="e.g., REG001",
                help="Enter the registration number from QR code",
                key="manual_reg"
            )
        
        with col2:
            manual_name = st.text_input(
                "Enter Name (optional):",
                placeholder="e.g., John Doe",
                help="Optional: Enter participant name",
                key="manual_name"
            )
        
        if st.button("✅ Mark Attendance Manually", use_container_width=True, key="manual_button") and manual_reg:
            if manual_name:
                qr_data = f"{manual_reg}_{manual_name}"
            else:
                qr_data = manual_reg
            
            process_qr_data(qr_data)


    st.markdown("---")
    st.markdown("### 📋 Recent Scanning Session")
    
    if st.session_state.marked_records:
        total_new = len([r for r in st.session_state.marked_records if r['status'] == 'Newly Marked'])
        total_already = len([r for r in st.session_state.marked_records if r['status'] == 'Already Present'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Newly Marked", total_new)
        with col2:
            st.metric("Already Present", total_already)
        
        st.markdown("#### Recent Activity:")
        for record in reversed(st.session_state.marked_records[-10:]):  # Show last 10
            if record['status'] == 'Newly Marked':
                st.markdown(f"✅ **{record['name']}** ({record['reg_num']}) - {record['time']}")
            else:
                st.markdown(f"⚠️ **{record['name']}** ({record['reg_num']}) - Already Present - {record['time']}")
    else:
        st.write("No attendees marked yet in this session.")

    # Show overall statistics
    try:
        worksheet = get_google_sheet()
        data = worksheet.get_all_records()
        
        present_count = len([row for row in data if row.get('Status', '').lower() == 'present'])
        total_count = len(data)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Participants", total_count)
        
        with col2:
            st.metric("Overall Present", present_count)
        
        # Progress bar
        if total_count > 0:
            attendance_rate = (present_count / total_count) * 100
            st.progress(attendance_rate / 100)
            st.caption(f"Overall Attendance Rate: {attendance_rate:.1f}%")
        
    except Exception as e:
        st.error(f"Could not load attendance data: {str(e)}")

    with st.expander("❓ Troubleshooting Tips", expanded=False):
        st.markdown("""
        ### If camera is not working:
        
        1. **Check camera permissions** in your browser/system
        2. **Close other applications** using the camera
        3. **Try a different browser** (Chrome works best)
        4. **Use manual entry** as alternative
        5. **Restart the application**
        
        ### Common QR scanning issues:
        - QR code too far from camera
        - Poor lighting conditions
        - QR code damaged or unclear
        - Camera out of focus
        
        ### Error messages explained:
        - **"Camera index out of range"**: OpenCV can't find the selected camera
        - **"Assertion failed"**: ZBar library warning (can be ignored)
        - **"obsensor" errors**: Related to 3D cameras (not affecting functionality)
        """)