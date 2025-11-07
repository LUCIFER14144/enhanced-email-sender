# 🚀 Enhanced Email Sender - Deployment Guide

Complete step-by-step guide to deploy your cloud-enabled email sender system.

## 📋 Prerequisites

- [Vercel Account](https://vercel.com) (free tier available)
- [Supabase Account](https://supabase.com) (free tier available)
- [GitHub Account](https://github.com) (for code hosting)
- Vercel CLI installed: `npm i -g vercel`

## 🗄️ Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create new project:
   - **Name**: `enhanced-email-sender`
   - **Password**: Choose strong database password
   - **Region**: Select closest to your users

### 1.2 Run Database Schema
1. In Supabase dashboard, go to **SQL Editor**
2. Copy contents of `database/schema.sql`
3. Paste and click **Run**
4. Verify tables are created in **Table Editor**

### 1.3 Get Connection Details
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public key**: `eyJ...`
   - **service_role key**: `eyJ...` (keep secret!)

## 🚀 Step 2: Deploy to Vercel

### 2.1 Connect GitHub Repository
1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/email-sender.git
   git push -u origin main
   ```

### 2.2 Deploy with Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **New Project**
3. Import your GitHub repository
4. Configure deployment:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty)
   - **Output Directory**: `api`

### 2.3 Set Environment Variables
In Vercel dashboard → **Settings** → **Environment Variables**, add:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
JWT_SECRET=your-super-secret-32-character-minimum-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
```

**Generate JWT Secret:**
```bash
# Generate secure 32+ character secret
openssl rand -base64 32
```

### 2.4 Deploy
1. Click **Deploy**
2. Wait for deployment to complete
3. Get your deployment URL: `https://your-app.vercel.app`

## ✅ Step 3: Test Deployment

### 3.1 Test API Health
```bash
curl https://your-app.vercel.app/
```
Expected response:
```json
{
  "message": "Enhanced Email Sender API",
  "status": "active",
  "version": "1.0.0"
}
```

### 3.2 Test Admin Dashboard
1. Visit: `https://your-app.vercel.app/admin`
2. Login with your admin credentials
3. Verify dashboard loads correctly

### 3.3 Test User Registration
```bash
curl -X POST https://your-app.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "subscription_type": "free"
  }'
```

### 3.4 Test User Login
```bash
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

## 🖥️ Step 4: Desktop Application Setup

### 4.1 Update Desktop App Configuration
Edit `desktop/cloud_integration.py`, line 25:
```python
self.api_base_url = api_base_url or "https://your-app.vercel.app"
```

### 4.2 Create Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "EmailSender" --icon=icon.ico desktop/main.py

# Executable will be in dist/EmailSender.exe
```

### 4.3 Test Desktop Application
1. Run the executable: `dist/EmailSender.exe`
2. Enter your API URL: `https://your-app.vercel.app`
3. Login with test user credentials
4. Verify cloud sync works

## 👑 Step 5: Admin Management

### 5.1 Access Admin Dashboard
1. Go to: `https://your-app.vercel.app/admin`
2. Login with admin credentials
3. Dashboard should show:
   - User statistics
   - Add user form
   - User management table

### 5.2 Add Users via Admin Panel
1. Fill out "Add New User" form:
   - **Username**: unique identifier
   - **Password**: secure password
   - **Email**: user's email (optional)
   - **Subscription**: free, premium, enterprise
   - **Days**: subscription duration
2. Click "Add User"
3. User appears in user table

### 5.3 Manage Subscriptions
- **Extend**: Add days to existing subscription
- **Set Date**: Set specific expiration date
- **View Data**: See user's recipients and campaigns
- **Delete**: Remove user and all data

## 🔧 Step 6: Customization

### 6.1 Branding
Update these files with your branding:
- `admin/templates/admin_login.html` - Admin login page
- `admin/templates/admin_dashboard.html` - Admin dashboard
- `desktop/main.py` - Desktop app title and branding

### 6.2 Email Integration
To integrate your existing email sending logic:
1. Copy your email functions to `desktop/main.py`
2. Replace the placeholder `send_email()` method
3. Add SMTP configuration to settings

### 6.3 Custom Domain (Optional)
1. In Vercel dashboard → **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. Update desktop app API URL

## 📊 Step 7: Monitoring & Maintenance

### 7.1 Monitor Usage
- Check Vercel dashboard for function invocations
- Monitor Supabase dashboard for database usage
- Review user activity in admin panel

### 7.2 Backup Database
```sql
-- Export users
SELECT * FROM users;

-- Export recipient lists
SELECT * FROM recipient_lists;

-- Export campaigns
SELECT * FROM email_campaigns;
```

### 7.3 Update Application
1. Make changes to code
2. Push to GitHub: `git push`
3. Vercel auto-deploys from main branch
4. Update desktop app and redistribute

## 🚨 Troubleshooting

### Common Issues

**"Invalid token" errors:**
- Check JWT_SECRET is set correctly
- Ensure secret is 32+ characters
- Verify environment variables are saved

**Database connection errors:**
- Verify Supabase URL and keys
- Check database is running
- Confirm tables exist

**Admin login fails:**
- Check ADMIN_USERNAME and ADMIN_PASSWORD
- Verify environment variables
- Try incognito/private browsing

**Desktop app can't connect:**
- Verify API URL is correct
- Check internet connection
- Test API endpoints manually

### Performance Optimization

**For high usage:**
- Upgrade Vercel plan for higher limits
- Upgrade Supabase for more database connections
- Implement caching for frequent requests
- Add rate limiting

## 📞 Support

### For Users
- Provide them with download link to executable
- Give them the API URL for cloud login
- Share basic usage instructions

### For Admins
- Access admin panel: `https://your-app.vercel.app/admin`
- Monitor via Vercel and Supabase dashboards
- Check logs for errors and usage patterns

## 🎉 Launch Checklist

- [ ] Database schema created in Supabase
- [ ] Environment variables set in Vercel
- [ ] API deployed and responding
- [ ] Admin dashboard accessible
- [ ] Test user can register and login
- [ ] Desktop app connects to cloud
- [ ] Email sending integration complete
- [ ] Branding and customization applied
- [ ] User documentation prepared
- [ ] Admin access configured

## 🌟 Features Summary

Your deployed system now includes:

### ✅ Cloud Backend
- JWT authentication with expiration
- User-specific data storage
- Subscription management
- Real-time validation
- Campaign tracking

### ✅ Admin Dashboard
- Web-based user management
- Subscription control
- Usage monitoring
- Secure admin access
- Modern responsive UI

### ✅ Desktop Application
- Cloud authentication
- Data synchronization
- Offline capability
- Subscription monitoring
- Professional GUI

### ✅ Security
- Password hashing (bcrypt)
- JWT tokens with expiration
- Admin role separation
- Input validation
- CORS protection

**🎊 Congratulations! Your Enhanced Email Sender system is now live and ready to use!**

---

**Need help?** Check the troubleshooting section or review the API documentation at `https://your-app.vercel.app/docs`