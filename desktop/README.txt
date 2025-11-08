# Enhanced Email Sender - Quick Start Guide

## 📦 Installation Steps

### Step 1: Extract the ZIP
Extract all files to a folder on your computer (e.g., `C:\EmailSender\`)

### Step 2: Setup wkhtmltopdf (Required for PDF/Image features)
1. **Right-click** on `SETUP_WKHTMLTOPDF.bat`
2. Select **"Run as administrator"**
3. Wait for the setup to complete
4. Press any key to close the window

> ⚠️ **Important**: Running as administrator ensures proper PATH configuration

### Step 3: Run the Application
1. Double-click `Enhanced-Email-Sender.exe`
2. Sign in with your credentials provided by admin
3. Start sending emails!

---

## 🔒 Security Features

### Built-in Security:
- ✅ Encrypted cloud communication (HTTPS)
- ✅ Secure authentication tokens (JWT)
- ✅ Password hashing (bcrypt)
- ✅ Session management
- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ XSS attack prevention

### Best Practices:
- 🔐 Keep your login credentials secure
- 🔄 Change password regularly through admin
- 🚫 Don't share your account
- 📧 Verify email recipients before sending
- 🔍 Check subscription status regularly

---

## 📂 Folder Structure

```
Enhanced-Email-Sender/
│
├── Enhanced-Email-Sender.exe    (Main application)
├── SETUP_WKHTMLTOPDF.bat        (wkhtmltopdf installer)
├── README.txt                    (This file)
│
├── wkhtmltopdf/                  (PDF/Image conversion tool)
│   └── bin/
│       ├── wkhtmltopdf.exe
│       └── wkhtmltoimage.exe
│
├── Elements/                     (Auto-created on first run)
│   ├── charges.csv
│   ├── number.csv
│   ├── product.csv
│   └── quantity.csv
│
├── Invoices/                     (Generated invoices)
└── PDF/                          (Generated PDFs)
```

---

## ⚡ Quick Troubleshooting

### "wkhtmltopdf not found" error?
→ Run `SETUP_WKHTMLTOPDF.bat` as administrator

### Windows SmartScreen warning?
→ Click "More info" → "Run anyway"
→ This is a false positive (unsigned application)

### Can't login?
→ Contact your administrator for credentials
→ Ensure internet connection is active

### Cloud Sync not working?
→ Check internet connection
→ Verify subscription is active
→ Click "Refresh Days" button

---

## 🆘 Support

For technical issues or questions:
- Contact your system administrator
- Check admin dashboard for subscription status
- Ensure all files from ZIP are extracted

---

## 📝 System Requirements

- Windows 10 or 11 (64-bit)
- 4GB RAM minimum
- Internet connection (for cloud features)
- 200MB free disk space

---

## 🔐 Security Notice

This application uses:
- End-to-end HTTPS encryption
- Secure token-based authentication
- Industry-standard password hashing
- Protected cloud storage

**Never share your credentials with anyone!**

---

*Enhanced Email Sender v1.0.0 - November 2025*
