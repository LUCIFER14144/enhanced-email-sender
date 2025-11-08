# How to Create a GitHub Release for Downloads

## 📦 Why We Need a Release

GitHub has a 100MB file size limit for regular files in repositories. Our EXE and ZIP files are ~82MB each, which exceeds this limit when pushed normally. GitHub Releases allow hosting larger files (up to 2GB per file).

## 🚀 Steps to Create a Release

### Option 1: Using GitHub Web Interface (Easiest)

1. **Go to GitHub Repository**
   - Visit: https://github.com/LUCIFER14144/enhanced-email-sender

2. **Navigate to Releases**
   - Click "Releases" on the right sidebar
   - Click "Create a new release" (or "Draft a new release")

3. **Create Tag**
   - Tag version: `v1.0.0` (or any version you want)
   - Target: `main` branch
   - Release title: `Enhanced Email Sender v1.0.0`

4. **Add Description**
   ```markdown
   ## 🎉 Enhanced Email Sender v1.0.0
   
   Professional desktop email client with cloud integration.
   
   ### ✨ Features
   - ✅ Cloud sync for settings and recipients
   - ✅ Subscription management with days tracking
   - ✅ Professional email sending with HTML/PDF support
   - ✅ Standalone executable - no Python required
   - ✅ wkhtmltopdf installer included
   
   ### 📥 Downloads
   - **Enhanced-Email-Sender.zip** (Recommended) - Extract and run
   - **Enhanced-Email-Sender.exe** - Direct executable
   
   ### 📋 System Requirements
   - Windows 10/11 (64-bit)
   - 4GB RAM minimum
   - 200MB free disk space
   - Internet connection for cloud features
   
   ### 🔧 Installation
   1. Download the ZIP file
   2. Extract to a folder
   3. Read SETUP_INSTRUCTIONS.txt
   4. Run INSTALL_WKHTMLTOPDF.bat (optional, for best quality)
   5. Double-click Enhanced-Email-Sender.exe
   
   ### 📝 What's Included
   - Enhanced-Email-Sender.exe
   - SETUP_INSTRUCTIONS.txt
   - INSTALL_WKHTMLTOPDF.bat
   - wkhtmltopdf installer files
   - Sample data folders
   ```

5. **Upload Files**
   - Drag and drop or click "Attach binaries"
   - Upload: `desktop/dist/Enhanced-Email-Sender.exe`
   - Upload: `desktop/dist/Enhanced-Email-Sender.zip`
   - Wait for upload to complete (may take a few minutes for 82MB files)

6. **Publish**
   - Check "Set as the latest release"
   - Click "Publish release"

---

### Option 2: Using GitHub CLI (Faster)

If you have GitHub CLI installed:

```powershell
# Navigate to project
cd "c:\Users\Eliza\Desktop\perfected vercelblasting"

# Create release and upload files
gh release create v1.0.0 `
  desktop/dist/Enhanced-Email-Sender.exe `
  desktop/dist/Enhanced-Email-Sender.zip `
  --title "Enhanced Email Sender v1.0.0" `
  --notes "Professional desktop email client with cloud integration. See README for details." `
  --latest
```

Install GitHub CLI from: https://cli.github.com/

---

## ✅ After Creating the Release

Once the release is created, the download page will automatically work:

- **ZIP Download**: `https://github.com/LUCIFER14144/enhanced-email-sender/releases/latest/download/Enhanced-Email-Sender.zip`
- **EXE Download**: `https://github.com/LUCIFER14144/enhanced-email-sender/releases/latest/download/Enhanced-Email-Sender.exe`

The download page has built-in fallback logic:
- If the release exists: Direct download starts
- If not found: Opens releases page with instructions

## 🔄 Updating the Release

When you rebuild the EXE/ZIP with updates:

1. Create a new tag (e.g., `v1.0.1`, `v1.1.0`)
2. Upload new files
3. Mark as "latest release"
4. Download page automatically points to latest version

---

## 📊 Current File Information

- **EXE Size**: 81.87 MB
- **ZIP Size**: 81.08 MB
- **SHA256 (EXE)**: 36D68A24DF32F734EB5DB8BF1B4D100E7D9DD37536950721DD12885AAB8F94B2
- **SHA256 (ZIP)**: DFF543A694759952724F7E643A3899A43F37D87BDB89EA4D54EC10973FA2D5F2

---

## 🌐 Production URLs

**Download Page**: https://perfected-vercelblasting-g7xua2wt3-mds-projects-f21afbac.vercel.app/download

**Admin Panel**: https://perfected-vercelblasting-g7xua2wt3-mds-projects-f21afbac.vercel.app/admin
