# 📧 Enhanced Email Sender - Cloud Edition

A complete cloud-enabled email sender system with desktop application, admin dashboard, and subscription management.

## 🌟 Features

### ☁️ Cloud Backend
- **FastAPI REST API** with JWT authentication
- **User management** with subscription expiration
- **Real-time validation** of user accounts
- **Cloud data storage** for recipients and settings
- **Campaign tracking** and usage statistics
- **Subscription management** with expiration dates

### 🖥️ Desktop Application
- **Cloud authentication** - Users login with cloud credentials
- **Data synchronization** - Sync recipients across devices
- **Offline capable** - Works without internet, syncs when online
- **Subscription monitoring** - Real-time expiration checking
- **Modern GUI** - Professional tkinter interface

### 👑 Admin Dashboard
- **Web-based admin panel** accessible from anywhere
- **User management** - Add, delete, view user data
- **Subscription control** - Set expiration dates, extend subscriptions
- **Usage monitoring** - Track campaigns and email sending
- **Secure authentication** - Admin-only access

## 🚀 Quick Start

### 1. Database Setup (Supabase)

1. Create a [Supabase](https://supabase.com) account
2. Create a new project
3. Run the SQL schema from `database/schema.sql`
4. Get your project URL and API keys

### 2. Environment Variables

Set these in your Vercel dashboard:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
JWT_SECRET=your-super-secret-32-char-minimum-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
```

### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
vercel --prod

# Set environment variables
vercel env add SUPABASE_URL production
vercel env add SUPABASE_ANON_KEY production
vercel env add SUPABASE_SERVICE_KEY production
vercel env add JWT_SECRET production
vercel env add ADMIN_USERNAME production
vercel env add ADMIN_PASSWORD production
```

### 4. Test the Deployment

- **API Health**: `https://your-app.vercel.app/`
- **Admin Login**: `https://your-app.vercel.app/admin`
- **Documentation**: `https://your-app.vercel.app/docs`

## 📱 Desktop Application

### Installation

1. **Download the application** from your distribution link
2. **Install Python dependencies**:
   ```bash
   pip install -r desktop/requirements.txt
   ```

### Running the Desktop App

```bash
python desktop/main.py
```

### Creating Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "EmailSender" desktop/main.py

# Executable will be in dist/ folder
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/status` - Check user status

### Recipients Management
- `POST /api/recipients/save` - Save recipient list
- `GET /api/recipients/load` - Load user's recipient lists
- `DELETE /api/recipients/delete/{list_id}` - Delete recipient list

### Settings
- `POST /api/settings/save` - Save user settings
- `GET /api/settings/load` - Load user settings

### Admin Endpoints
- `GET /admin` - Admin login page
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/users/add` - Add new user
- `POST /admin/users/{user_id}/extend` - Extend user subscription
- `DELETE /admin/users/{user_id}` - Delete user

## 👑 Admin Dashboard Usage

### Access the Dashboard
1. Navigate to `https://your-app.vercel.app/admin`
2. Login with admin credentials
3. Manage users and subscriptions

### Managing Users
- **Add Users**: Fill form with username, password, email, subscription type
- **Set Expiration**: Set specific expiration dates
- **Extend Subscriptions**: Add days to existing subscriptions
- **View User Data**: See recipients, campaigns, settings
- **Delete Users**: Remove users and all their data

### Subscription Management
- **Individual Expiration**: Each user has their own expiration date
- **Real-time Validation**: Users checked on login and periodically
- **Automatic Logout**: Desktop app closes when subscription expires
- **Warning System**: Users notified before expiration

## 🔒 Security Features

- **JWT Authentication** with expiration
- **Bcrypt Password Hashing**
- **Admin Role Separation**
- **CORS Protection**
- **Input Validation**
- **SQL Injection Prevention**

## 📊 Database Schema

```sql
-- Users with subscription management
users (id, username, hashed_password, email, subscription_type, expires_at, is_active, ...)

-- User-specific recipient lists
recipient_lists (id, user_id, list_name, recipients, created_at, updated_at)

-- User settings storage
user_settings (id, user_id, settings, updated_at)

-- Email campaign tracking
email_campaigns (id, user_id, campaign_name, status, total_emails, sent_emails, ...)

-- Usage logs
usage_logs (id, user_id, action, details, created_at)
```

## 🚀 Deployment Architecture

```
Desktop App (Windows/Mac/Linux)
    ↕ HTTPS API Calls
Cloud Backend (Vercel)
    ↕ SQL Queries  
Database (Supabase PostgreSQL)
    ↔ Admin Dashboard (Web)
```

## 📋 User Workflow

1. **Download** desktop app from your link
2. **Launch app** → Cloud login window appears
3. **Enter credentials** → Verified against cloud database
4. **App opens** → Loads user's cloud data automatically
5. **Work normally** → Save/load recipients from cloud
6. **Data persists** → Available from any device with login

## 🛠️ Development

### Local Development

```bash
# Backend
cd api
pip install -r requirements.txt
uvicorn main:app --reload

# Desktop App
cd desktop
pip install -r requirements.txt
python main.py
```

### Testing

```bash
# Test API endpoints
curl https://your-app.vercel.app/
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

## 📈 Monitoring

- **User Activity**: Track logins, email sending, data uploads
- **Subscription Status**: Monitor active/expired users
- **Usage Statistics**: Campaign success rates, recipient counts
- **Error Logging**: API errors and desktop app issues

## 🔧 Customization

### Adding New Features
1. **API**: Add endpoints in `api/main.py`
2. **Database**: Update schema in `database/schema.sql`
3. **Desktop**: Modify `desktop/main.py`
4. **Admin**: Update templates in `admin/templates/`

### Branding
- Update application titles and descriptions
- Modify color schemes in templates
- Add custom logos and icons
- Customize email templates

## 📞 Support

### For Users
- Check subscription status in desktop app
- Contact admin for account issues
- Use offline mode if cloud is unavailable

### For Admins
- Monitor user activity in dashboard
- Extend subscriptions as needed
- View user data and troubleshoot issues
- Manage system-wide settings

## 📄 License

This project is proprietary software. Unauthorized distribution is prohibited.

---

**Enhanced Email Sender v1.0** - Cloud-enabled email marketing solution with subscription management.