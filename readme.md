# 📊 QR Code Attendance System

A comprehensive web-based attendance management system that uses QR codes for participant tracking. Built with Streamlit and integrated with Google Sheets for real-time data synchronization.

## 🚀 Features

### ✅ Core Functionality
- **QR Code Scanning**: Real-time camera scanning for attendance marking
- **Duplicate Prevention**: Prevents multiple entries for same participant
- **Google Sheets Integration**: Automatic data sync with cloud spreadsheet
- **QR Code Generation**: Create unique QR codes for each participant
- **Attendance Analytics**: Visual charts, statistics, and reports
- **Export Functionality**: Download data as CSV or Excel files
- **Manual Entry Option**: Alternative to QR scanning

### 🎯 Key Benefits
- **Real-time Updates**: Live attendance tracking
- **No Duplicates**: Smart duplicate detection
- **Easy Deployment**: Simple setup process
- **Responsive UI**: Modern, user-friendly interface
- **Secure**: Google Sheets authentication

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- Google Account (for Google Sheets API)
- Webcam (for QR scanning)
- Internet connection

## 🛠️ Installation

### Step 1: Clone/Download the Project
### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
### Step 3: Run the Application
```bash
streamlit run main.py
```

## 📱 How to Use

### 1. Generate QR Codes
**For Single Participant:**
1. Navigate to **Generate QR** page
2. Select **Single QR** tab
3. Enter participant's name and registration number
4. Click **Generate QR Code**
5. Download and print the QR code

**For Multiple Participants:**
1. Prepare a CSV file with columns:
   - `Name`
   - `Registration_Number`
2. Go to **Bulk QR** tab
3. Upload the CSV file
4. Click **Generate All QR Codes**
5. Download individual QR codes from **Existing Data** tab

### 2. Mark Attendance
**Using QR Scanner:**
1. Navigate to **Mark Attendance** page
2. Select your camera from dropdown
3. Click **Start Scanner**
4. Hold QR code in front of camera
5. Wait for confirmation message
6. Click **Stop Scanner** when done

**Manual Entry:**
1. Expand **Manual Entry** section
2. Enter registration number
3. (Optional) Enter participant name
4. Click **Mark Attendance Manually**

### 3. View Analytics
1. Navigate to **View Analysis** page
2. See overall statistics
3. View data table with search
4. Analyze visual charts
5. Export data as needed

## 🗂️ File Structure
```
attendance_system/
├── main.py                          # Main application entry point
├── utils.py                         # Google Sheets utilities
├── pages/
│   ├── Mark_Attendance.py           # QR scanning page
│   ├── Generate_QR.py              # QR generation page
│   └── View_Analysis.py            # Analytics page
├── encoded_creds.txt               # Base64 encoded credentials
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Configuration

### Google Sheets Structure
The system expects the following structure:
- **Sheet Name**: Task1
- **Columns**: 
  - Column A: Name
  - Column B: Registration_Number
  - Column C: Status (Present/Absent)

# Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Camera Not Working
```
Error: Camera index out of range
```
**Solutions:**
- Check camera permissions
- Close other applications using camera
- Try different browser (Chrome recommended)
- Use manual entry as alternative

#### 2. Google Sheets Connection Error
```
Error: Failed to connect to Google Sheets
```
**Solutions:**
- Verify encoded_creds.txt exists
- Check internet connection
- Ensure sheet is shared with service account
- Verify sheet ID is correct

#### 3. QR Code Not Scanning
```
Error: No QR code detected
```
**Solutions:**
- Ensure good lighting
- Hold QR code steady
- Keep QR code parallel to camera
- Try generating new QR code

#### 4. "Already Present" Warning
When a participant is already marked present, the system shows:
- Yellow warning message
- Participant details
- Status: "Already Present"

## 📊 Usage Examples

### Example 1: Event Registration
1. Generate QR codes for all registered participants
2. Distribute QR codes at registration desk
3. Scan QR codes at event entry
4. Monitor real-time attendance

### Example 2: Classroom Attendance
1. Generate QR codes for each student
2. Students scan QR codes when entering class
3. Export attendance report after class
4. Identify absent students

### Example 3: Workshop Tracking
1. Create participant list
2. Generate QR codes
3. Track arrival times
4. Generate attendance certificates

## 🔐 Security Notes

1. **Credentials Security**: Never commit `encoded_creds.txt` to public repositories
2. **Sheet Permissions**: Use read/write permissions only for service account
3. **Data Privacy**: Ensure participant data complies with privacy regulations
4. **Network Security**: Use HTTPS in production deployment

### Local Network
```bash
# Run on local network
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## 🙏 Acknowledgments

- Streamlit team for amazing framework
- Google for Sheets API
- Open source contributors

---

## 🚀 Quick Start Summary

```bash
# 1. Install
pip install -r requirements.txt

# 2. Setup Google Sheets
# - Create service account
# - Encode credentials
# - Share spreadsheet

# 3. Run
streamlit run main.py

# 4. Access
# Open browser: http://localhost:8501
```

---

**Happy Tracking!** 🎯

For more information or support, please refer to the documentation or contact the development team.