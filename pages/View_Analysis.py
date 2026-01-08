import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import get_google_sheet
import io

def show():
    st.markdown('<h1 class="main-header">📊 Attendance Analysis</h1>', unsafe_allow_html=True)

    try:
        # Get data from Google Sheets
        worksheet = get_google_sheet()
        data = worksheet.get_all_records()
        
        if not data:
            st.info("No attendance data available yet.")
            return
        
        df = pd.DataFrame(data)
        
        total = len(df)
        present = len(df[df['Status'].str.lower() == 'present'])
        absent = total - present
        attendance_rate = (present / total * 100) if total > 0 else 0
        
        st.markdown("### 📈 Overall Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Participants", total)
        with col2:
            st.metric("Present", present)
        with col3:
            st.metric("Absent", absent)
        with col4:
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        
        st.progress(attendance_rate / 100)
        
        tab1, tab2, tab3 = st.tabs(["📋 Data Table", "📈 Visualizations", "📤 Export"])
        
        with tab1:
            st.markdown("### Complete Attendance Data")
            
            search = st.text_input("🔍 Search by name or registration number:")
            if search:
                filtered_df = df[
                    df['Name'].str.contains(search, case=False, na=False) |
                    df['Registration_Number'].str.contains(search, case=False, na=False)
                ]
            else:
                filtered_df = df
            
            filtered_present = len(filtered_df[filtered_df['Status'] == 'Present'])
            filtered_total = len(filtered_df)
            
            if filtered_total > 0:
                st.caption(f"Showing {filtered_total} records ({filtered_present} present, {filtered_total - filtered_present} absent)")
            
            def color_status(val):
                if val == 'Present':
                    return 'background-color: #D1FAE5; color: #065F46'
                else:
                    return 'background-color: #FEE2E2; color: #991B1B'
            
            styled_df = filtered_df.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True, height=500)
            
            st.markdown("### 📊 Quick Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top 5 Present Participants:**")
                present_df = filtered_df[filtered_df['Status'] == 'Present'].head()
                if not present_df.empty:
                    st.dataframe(present_df[['Name', 'Registration_Number']], use_container_width=True)
                else:
                    st.info("No present participants found")
            with col2:
                st.markdown("**Top 5 Absent Participants:**")
                absent_df = filtered_df[filtered_df['Status'] == 'Absent'].head()
                if not absent_df.empty:
                    st.dataframe(absent_df[['Name', 'Registration_Number']], use_container_width=True)
                else:
                    st.info("No absent participants found")
        
        with tab2:
            st.markdown("### Visual Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                status_counts = df['Status'].value_counts()
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Attendance Distribution",
                    color=status_counts.index,
                    color_discrete_map={'Present': '#10B981', 'Absent': '#EF4444'},
                    hole=0.3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_bar = px.bar(
                    x=['Present', 'Absent'],
                    y=[present, absent],
                    title="Attendance Count",
                    color=['Present', 'Absent'],
                    color_discrete_map={'Present': '#10B981', 'Absent': '#EF4444'},
                    labels={'x': 'Status', 'y': 'Count'},
                    text=[present, absent]
                )
                fig_bar.update_layout(showlegend=False)
                fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("### 🎯 Attendance Rate Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=attendance_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Attendance Percentage", 'font': {'size': 24}},
                delta={'reference': 90, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#3B82F6"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': 'red'},
                        {'range': [50, 75], 'color': 'yellow'},
                        {'range': [75, 100], 'color': 'green'}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with tab3:
            st.markdown("### Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📥 Export Formats:**")
                
                # CSV Export
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"attendance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="csv_export",
                    use_container_width=True
                )
                
                # Excel Export
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Attendance')
                
                st.download_button(
                    label="Download as Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"attendance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="excel_export",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("**🔍 Filtered Export:**")
                
                # Filter by status
                status_filter = st.multiselect(
                    "Select status to export:",
                    options=['Present', 'Absent'],
                    default=['Present', 'Absent'],
                    key="export_filter"
                )
                
                if status_filter:
                    filtered_df = df[df['Status'].isin(status_filter)]
                    filtered_csv = filtered_df.to_csv(index=False)
                    
                    st.download_button(
                        label=f"Download Filtered ({len(filtered_df)} records)",
                        data=filtered_csv,
                        file_name=f"filtered_attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="filtered_export",
                        use_container_width=True
                    )
            
            st.markdown("---")
            st.markdown("### 📋 Report Summary")
            
            report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            report_html = f"""
            <div class="info-message">
            <h3>Attendance Report</h3>
            <p><strong>Generated on:</strong> {report_time}</p>
            <p><strong>Total Participants:</strong> {total}</p>
            <p><strong>Present:</strong> {present} ({attendance_rate:.1f}%)</p>
            <p><strong>Absent:</strong> {absent} ({100-attendance_rate:.1f}%)</p>
            <hr>
            <p><strong>Recommendations:</strong></p>
            """
            
            if attendance_rate >= 90:
                report_html += "<p>✅ <strong>Excellent attendance!</strong> Event is well-attended.</p>"
            elif attendance_rate >= 70:
                report_html += "<p>⚠️ <strong>Good attendance</strong>, but there's room for improvement.</p>"
            else:
                report_html += "<p>❌ <strong>Low attendance</strong>, consider sending reminders or follow-ups.</p>"
            
            report_html += "</div>"
            
            st.markdown(report_html, unsafe_allow_html=True)
        
        # Real-time updates
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
        <h3>❌ Error Loading Analysis Data</h3>
        <p>Error: {str(e)}</p>
        <p>Make sure you have proper Google Sheets connection setup.</p>
        </div>
        """, unsafe_allow_html=True)