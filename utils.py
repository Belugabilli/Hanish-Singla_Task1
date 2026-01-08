import gspread
from google.oauth2.service_account import Credentials
import base64
import json
import os

def get_google_sheet():
    """Initialize and return Google Sheet connection"""
    try:
        if not os.path.exists('encoded_creds.txt'):
            raise Exception("encoded_creds.txt not found. Please add your encoded Google Service Account credentials.")
        
        with open('encoded_creds.txt', 'r') as f:
            encoded_creds = f.read().strip()
        
        decoded_creds = base64.b64decode(encoded_creds).decode()
        service_account_info = json.loads(decoded_creds)
        
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scope
        )
        
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key('19tMX_CiRvB0yBjbgt_MJlLg0fY0guQ0vehJQvkSBVo8')
        worksheet = sheet.worksheet('Task1')
        
        headers = worksheet.row_values(1)
        expected_headers = ['Name', 'Registration_Number', 'Status']
        
        if not headers or headers != expected_headers:
            worksheet.clear()
            worksheet.append_row(expected_headers)
        
        return worksheet
    
    except Exception as e:
        raise Exception(f"Failed to connect to Google Sheets: {str(e)}")

def check_duplicate(worksheet, registration_number):
    """Check if registration number already exists in sheet"""
    try:
        data = worksheet.get_all_records()
        for row in data:
            if str(row.get('Registration_Number', '')).strip() == str(registration_number).strip():
                return True, row
        return False, None
    except Exception as e:
        raise Exception(f"Error checking duplicate: {str(e)}")

def mark_attendance(worksheet, registration_number):
    """Mark participant as present"""
    try:
        data = worksheet.get_all_values()

        for i, row in enumerate(data[1:], start=2):  
            if len(row) >= 2 and str(row[1]).strip() == str(registration_number).strip():
                # Check if already marked as present
                if len(row) >= 3 and row[2] == "Present":
                    return "already_present", row[0] if len(row) > 0 else "Unknown"
                
                # Update status to Present
                worksheet.update_cell(i, 3, 'Present')
                return "marked", row[0] if len(row) > 0 else "Unknown"
        
        return "not_found", None
    except Exception as e:
        raise Exception(f"Error marking attendance: {str(e)}")

def get_attendance_data(worksheet):
    """Get all attendance data"""
    try:
        return worksheet.get_all_records()
    except Exception as e:
        raise Exception(f"Error getting data: {str(e)}")