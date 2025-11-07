# 🚀 Quick Deployment Guide

Your Enhanced Email Sender is now on GitHub: **https://github.com/LUCIFER14144/enhanced-email-sender**

## ⚡ Quick Deploy (2 Steps)

### Step 1: Set up Supabase Database (5 minutes)

1. **Go to [supabase.com](https://supabase.com)** → Create account/Sign in
2. **Click "New Project"**:
   - Name: `enhanced-email-sender`
   - Password: Choose strong password
   - Region: Select closest to you
3. **Wait 2-3 minutes** for project creation
4. **Set up database**:
   - Go to **SQL Editor** in Supabase dashboard
   - Copy entire content from `database/schema.sql`
   - Paste and click **Run**
5. **Get your keys**:
   - Go to **Settings** → **API**
   - Copy: Project URL, anon key, service_role key

### Step 2: Deploy to Vercel (2 minutes)

1. **Go to [vercel.com](https://vercel.com)** → Sign in with GitHub
2. **Click "New Project"** → Import `enhanced-email-sender` repository
3. **Configure**:
   - Framework: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: `api`
4. **Set Environment Variables** (click Add):
   ```
   SUPABASE_URL = https://your-project-id.supabase.co
   SUPABASE_ANON_KEY = your-anon-key
   SUPABASE_SERVICE_KEY = your-service-key
   JWT_SECRET = generate-32-char-random-string
   ADMIN_USERNAME = admin
   ADMIN_PASSWORD = your-secure-password
   ```
5. **Click Deploy** → Wait 2 minutes

## 🎯 Generate JWT Secret

Run this in terminal to generate secure JWT secret:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

## ✅ Test Your Deployment

Your app will be at: `https://your-app-name.vercel.app`

- **API Health**: `https://your-app.vercel.app/`
- **Admin Dashboard**: `https://your-app.vercel.app/admin`
- **API Docs**: `https://your-app.vercel.app/docs`

## 🖥️ Update Desktop App

Edit `desktop/cloud_integration.py` line 25:
```python
self.api_base_url = "https://your-app.vercel.app"
```

## 📦 Create Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "EmailSender" desktop/main.py
```

**Your executable will be in `dist/EmailSender.exe`**

---

## 🆘 Need Help?

- **Database issues**: Check Supabase dashboard → Table Editor
- **Deploy issues**: Check Vercel dashboard → Functions tab for errors
- **Environment variables**: Vercel → Settings → Environment Variables

**You're ready to launch! 🎉**