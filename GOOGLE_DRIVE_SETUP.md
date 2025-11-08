# 📦 Upload Enhanced Email Sender to Google Drive

GitHub has a 25MB file size limit, but our files are 81MB. Use Google Drive instead!

## 🚀 Quick Steps:

### 1. Upload to Google Drive
1. Open: https://drive.google.com
2. Click **"+ New"** → **"File upload"**
3. Select this file:
   ```
   C:\Users\Eliza\Desktop\perfected vercelblasting\desktop\dist\Enhanced-Email-Sender.zip
   ```
4. Wait for upload to complete (81 MB)

### 2. Get Shareable Link
1. Right-click the uploaded file
2. Click **"Share"**
3. Click **"Change to anyone with the link"**
4. Set to **"Viewer"**
5. Click **"Copy link"**

### 3. Extract File ID from Link
Your link will look like:
```
https://drive.google.com/file/d/1XyZ_AbC123-DeFgHiJkL/view?usp=sharing
```

The **File ID** is the middle part: `1XyZ_AbC123-DeFgHiJkL`

### 4. Update Download Page
Open this file in VS Code:
```
admin/static/download.html
```

Find this line (around line 103):
```html
<a href="https://drive.google.com/file/d/YOUR_GOOGLE_DRIVE_LINK/view"
```

Replace `YOUR_GOOGLE_DRIVE_LINK` with your actual File ID

Example:
```html
<a href="https://drive.google.com/file/d/1XyZ_AbC123-DeFgHiJkL/view"
```

### 5. Deploy
Run in terminal:
```powershell
cd "c:\Users\Eliza\Desktop\perfected vercelblasting"
git add admin/static/download.html
git commit -m "Add Google Drive download link"
git push origin main
vercel --prod
```

## ✅ Done!
Users can now download from Google Drive through your download page!

---

## Alternative: Direct Google Drive Download Link

For better user experience, you can also use the direct download format:
```html
<a href="https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"
```

This will start the download immediately instead of showing the Google Drive preview page.
