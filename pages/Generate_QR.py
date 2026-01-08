import streamlit as st
import qrcode
from PIL import Image
import io
import base64
from utils import get_google_sheet, check_duplicate
import pandas as pd

def show():
    st.markdown('<h1 class="main-header">🔳 Generate QR Codes</h1>', unsafe_allow_html=True)
    if 'generated_qrs' not in st.session_state:
        st.session_state.generated_qrs = {}
    if 'recently_added' not in st.session_state:
        st.session_state.recently_added = []

    def generate_qr_code(data, registration_number):
        """Generate QR code image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        st.session_state.generated_qrs[registration_number] = img_bytes
        
        return img_bytes

    def get_image_download_link(img_bytes, filename):
        """Generate download link for image"""
        b64 = base64.b64encode(img_bytes).decode()
        return f'<a href="data:image/png;base64,{b64}" download="{filename}" style="display: inline-block; padding: 10px 20px; background-color: #3B82F6; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0;">📥 Download QR Code</a>'

    tab1, tab2, tab3 = st.tabs(["Single QR", "Bulk QR", "Existing Data"])

    with tab1:
        st.markdown("### Generate Single QR Code")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name:", key="single_name")
            reg_number = st.text_input("Registration Number:", key="single_reg")
            
            if st.button("Generate QR Code", key="generate_single", use_container_width=True):
                if not name or not reg_number:
                    st.error("Please enter both name and registration number!")
                else:
                    try:
                        worksheet = get_google_sheet()
                        is_duplicate, existing = check_duplicate(worksheet, reg_number)
                        
                        if is_duplicate:
                            st.markdown(f"""
                            <div class="warning-message">
                            <h3>⚠️ Registration Number Already Exists!</h3>
                            <p>Registration number <strong>{reg_number}</strong> already exists for <strong>{existing.get('Name', 'Unknown')}</strong>.</p>
                            <p>Status: {existing.get('Status', 'Unknown')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Add to Google Sheet
                            worksheet.append_row([name, reg_number, "Absent"])
                            
                            st.session_state.recently_added.append({
                                'name': name,
                                'reg_num': reg_number,
                                'time': pd.Timestamp.now().strftime("%H:%M:%S")
                            })
                            
                            qr_data = f"{reg_number}_{name}"
                            
                            # Generate QR code
                            img_bytes = generate_qr_code(qr_data, reg_number)
                            
                            # Success message
                            st.markdown(f"""
                            <div class="success-message">
                            <h3>✅ QR Code Generated Successfully!</h3>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>Registration:</strong> {reg_number}</p>
                            <p><strong>Status:</strong> Added to database</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.balloons()
                    
                    except Exception as e:
                        st.markdown(f"""
                        <div class="error-message">
                        <h3>❌ Error Generating QR Code</h3>
                        <p>Error: {str(e)}</p>
                        </div>
                        """, unsafe_allow_html=True)

        with col2:
            st.markdown("### Preview")
            if reg_number and name and reg_number in st.session_state.generated_qrs:
                st.image(st.session_state.generated_qrs[reg_number], 
                        caption=f"QR Code for {name}", 
                        width=250)
                
                # Download link
                st.markdown(get_image_download_link(
                    st.session_state.generated_qrs[reg_number], 
                    f"QR_{reg_number}_{name}.png"
                ), unsafe_allow_html=True)
            
            st.markdown("""
            ### ℹ️ QR Code Format:
            The QR code contains:
            ```
            RegistrationNumber_Name
            ```
            **Example:** `REG123_JohnDoe`
            
            ### 📌 Notes:
            1. Registration numbers must be unique
            2. QR codes are saved to Google Sheets
            3. Status is initially set to "Absent"
            4. QR can be scanned to mark attendance
            """)

    with tab2:
        st.markdown("### Bulk Generate QR Codes")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], 
                                        help="CSV should have columns: 'Name' and 'Registration_Number'")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded file:")
                st.dataframe(df.head(), use_container_width=True)
                
                if 'Name' not in df.columns or 'Registration_Number' not in df.columns:
                    st.error("CSV must contain 'Name' and 'Registration_Number' columns!")
                else:
                    if st.button("Generate All QR Codes", key="bulk_generate", use_container_width=True):
                        worksheet = get_google_sheet()
                        success_count = 0
                        duplicate_count = 0
                        error_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in enumerate(df.iterrows()):
                            _, data = row
                            name = str(data['Name'])
                            reg_num = str(data['Registration_Number'])
                            
                            status_text.text(f"Processing {idx+1}/{len(df)}: {name} ({reg_num})")
                            
                            try:
                                # Check duplicate
                                is_duplicate, _ = check_duplicate(worksheet, reg_num)
                                
                                if not is_duplicate:
                                    # Add to sheet
                                    worksheet.append_row([name, reg_num, "Absent"])
                                    
                                    # Generate QR
                                    qr_data = f"{reg_num}_{name}"
                                    generate_qr_code(qr_data, reg_num)
                                    
                                    # Add to recently added
                                    st.session_state.recently_added.append({
                                        'name': name,
                                        'reg_num': reg_num,
                                        'time': pd.Timestamp.now().strftime("%H:%M:%S")
                                    })
                                    
                                    success_count += 1
                                else:
                                    duplicate_count += 1
                            except:
                                error_count += 1
                            
                            progress_bar.progress((idx + 1) / len(df))
                        
                        status_text.empty()
                        
                        # Show results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Successfully Added", success_count, delta_color="normal")
                        with col2:
                            st.metric("Duplicates Skipped", duplicate_count)
                        with col3:
                            st.metric("Errors", error_count, delta_color="inverse")
                        
                        if success_count > 0:
                            st.success(f"✅ Successfully generated {success_count} QR codes!")
                            st.info(f"QR codes are stored in session. You can download them from the 'Existing Data' tab.")
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    with tab3:
        st.markdown("### Existing Participants")
        
        try:
            worksheet = get_google_sheet()
            data = worksheet.get_all_records()
            
            if data:
                df = pd.DataFrame(data)
                
                # Show statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Participants", len(df))
                with col2:
                    present = len(df[df['Status'] == 'Present'])
                    st.metric("Present", present)
                with col3:
                    st.metric("Absent", len(df) - present)
                
                search_term = st.text_input("🔍 Search by name or registration number:")
                if search_term:
                    filtered_df = df[
                        df['Name'].str.contains(search_term, case=False, na=False) |
                        df['Registration_Number'].str.contains(search_term, case=False, na=False)
                    ]
                else:
                    filtered_df = df
                
                # Display table with formatting
                def color_status(val):
                    if val == 'Present':
                        return 'background-color: #D1FAE5; color: #065F46; font-weight: bold'
                    else:
                        return 'background-color: #FEE2E2; color: #991B1B'
                
                styled_df = filtered_df.style.applymap(color_status, subset=['Status'])
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Regenerate QR option
                st.markdown("---")
                st.markdown("### Regenerate QR Code")
                
                selected_reg = st.selectbox(
                    "Select registration number to regenerate QR:",
                    options=df['Registration_Number'].tolist() if not df.empty else [],
                    key="regenerate_select"
                )
                
                if selected_reg and st.button("🔁 Regenerate QR", use_container_width=True):
                    participant = df[df['Registration_Number'] == selected_reg].iloc[0]
                    qr_data = f"{selected_reg}_{participant['Name']}"
                    img_bytes = generate_qr_code(qr_data, selected_reg)
                    
                    # Display
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(img_bytes, caption=f"QR for {participant['Name']}", width=200)
                    with col2:
                        st.success(f"✅ QR Code regenerated for {participant['Name']} ({selected_reg})")
                        st.markdown(get_image_download_link(
                            img_bytes,
                            f"QR_{selected_reg}_{participant['Name']}.png"
                        ), unsafe_allow_html=True)
                        st.info(f"**QR Data:** `{qr_data}`")
            
            else:
                st.info("No participants found. Add some using the Single or Bulk tabs.")
        
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    if st.session_state.recently_added:
        st.markdown("---")
        st.markdown("### 🆕 Recently Added")
        
        recent_df = pd.DataFrame(st.session_state.recently_added[-10:])  # Last 10
        st.dataframe(recent_df, use_container_width=True)