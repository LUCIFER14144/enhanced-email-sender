# Enhanced Email Sender - Installation Guide

## 📦 Quick Start

1. **Extract the ZIP file** to a folder on your computer
2. **Run SETUP.bat** (Right-click → Run as Administrator)
3. **Launch Enhanced-Email-Sender.exe**
4. **Login** with credentials provided by your admin

---

## 🔒 Security Features

### Built-in Security:
- ✅ **Encrypted credentials** - All passwords stored securely
- ✅ **Cloud authentication** - JWT token-based login
- ✅ **Session management** - Automatic timeout after inactivity
- ✅ **Input validation** - Protection against injection attacks
- ✅ **HTTPS only** - All cloud communication encrypted
- ✅ **No data logging** - Your emails are not stored on our servers

### Recommendations:
- Keep your login credentials safe
- Don't share your account with others
- Log out when not using the application
- Keep Windows Defender/antivirus enabled
- Only download from official sources

---

## 🛠️ Setup wkhtmltopdf (Optional but Recommended)

### Why do you need it?
For **high-quality PDF and image generation** from HTML templates.

### Installation Methods:

#### Method 1: Automatic (Recommended)
1. Double-click **SETUP.bat** (Right-click → Run as Administrator)
2. Follow the on-screen instructions
3. Restart the application

#### Method 2: Manual Download
1. Visit: https://wkhtmltopdf.org/downloads.html
2. Download: **"Windows (MSVC 2015) 64-bit"** (About 30MB)
3. Run the installer
4. Accept default installation path
5. Restart Enhanced-Email-Sender

#### Method 3: Portable (No Installation)
1. Download wkhtmltopdf installer
2. Extract to folder: `wkhtmltopdf\bin\` (next to the EXE)
3. Run SETUP.bat to configure PATH
4. Restart the application

### Without wkhtmltopdf:
The software **will still work** but:
- Lower quality PDF generation
- Reduced image conversion quality
- Some features show warnings

---

## 📋 System Requirements

- **OS:** Windows 10 or 11 (64-bit)
- **RAM:** 4GB minimum (8GB recommended)
- **Disk:** 200MB free space
- **Internet:** Required for cloud features
- **Display:** 1280x720 or higher

---

## 🚀 Features

### Cloud Integration:
- Sync settings across devices
- Save recipient lists to cloud
- Real-time subscription tracking
- Days remaining displayed in header

### Email Features:
- Bulk email sending
- HTML templates with inline images
- PDF attachments
- Recipient list management
- Send statistics tracking

### Security:
- Encrypted cloud storage
- Secure authentication
- Session management
- No email content logging

---

## 🔐 Privacy & Security

### What we collect:
- Username and encrypted password
- Email sent count (statistics only)
- Subscription status
- Last login time

### What we DON'T collect:
- Email content
- Recipient email addresses
- Attachment files
- Personal email credentials (Gmail/SMTP)

### Data Protection:
- All communication uses HTTPS/TLS
- Passwords are hashed with bcrypt
- JWT tokens expire after 24 hours
- No third-party tracking

---

## ❓ Troubleshooting

### Windows SmartScreen Warning
If you see "Windows protected your PC":
1. Click **"More info"**
2. Click **"Run anyway"**
3. This is normal for new software

### Antivirus False Positive
Some antivirus may flag the EXE:
1. This is a **false positive**
2. The software is safe (check SHA256 hash)
3. Add exception in your antivirus
4. Or use the ZIP version

### Login Issues
- Verify your credentials with admin
- Check internet connection
- Clear browser cache if using web admin
- Contact admin to reset password

### wkhtmltopdf Not Found
- Run SETUP.bat as administrator
- Or manually install from official site
- Software works without it (reduced quality)

### Application Won't Start
- Make sure you extracted the ZIP
- Check Windows Event Viewer for errors
- Verify .NET Framework 4.7.2+ is installed
- Contact support

---

## 📞 Support

For technical support:
- Contact your system administrator
- Check admin dashboard for announcements
- Email: support@yourdomain.com

---

## 📝 Version Information

**Version:** 1.0.0
**Release Date:** November 7, 2025
**Build:** Production

---

## ⚖️ License

This software is licensed to your organization.
Unauthorized distribution is prohibited.

By using this software, you agree to the Terms of Service and Privacy Policy.

---

## 🔄 Updates

The application checks for updates automatically.
When an update is available, you'll see a notification.

To update manually:
1. Download new version from admin panel
2. Close the old application
3. Replace the EXE file
4. Run the new version

---

**© 2025 Enhanced Email Sender. All rights reserved.**
