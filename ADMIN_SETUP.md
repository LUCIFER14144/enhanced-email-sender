# Admin Panel Setup Guide

This document provides comprehensive instructions for setting up and configuring the admin panel.

## Environment Variables

Create a `.env` file in the root directory with the following configuration:

```env
# Authentication
JWT_SECRET=your-super-secure-jwt-secret-key
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_admin_password

# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Email Configuration (Optional)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SYSTEM_EMAIL=noreply@yourdomain.com
```

## Database Setup

1. Create a new Supabase project
2. Navigate to the SQL Editor
3. Execute the following scripts in order:
   ```bash
   database/complete_setup.sql   # Creates all tables and indexes
   database/insert_data.sql      # Inserts initial data (if needed)
   ```

## Installation

1. Install project dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the development server:
```bash
uvicorn api.main:app --reload
```

3. Access the admin interface:
- Login: http://localhost:8000/admin/login
- Dashboard: http://localhost:8000/admin/dashboard

## Features

### 1. User Management
- Create, update, and delete users
- Manage subscription tiers
- Set email sending limits
- Track usage statistics
- View user activity logs

### 2. Email Templates
- Create reusable email templates
- HTML and plain text support
- Template variables
- Preview functionality

### 3. Campaign Management
- Create and schedule campaigns
- Track delivery status
- View open and click rates
- Manage recipient lists

### 4. System Settings
- Configure default limits
- Set up SMTP settings
- Manage feature access by tier
- Control system-wide parameters

## API Endpoints

### Authentication
```
POST /admin/login
GET /admin/logout
```

### User Management
```
GET /api/admin/users
POST /api/admin/users
PUT /api/admin/users/{user_id}
DELETE /api/admin/users/{user_id}
```

### Templates
```
GET /api/admin/templates
POST /api/admin/templates
PUT /api/admin/templates/{template_id}
DELETE /api/admin/templates/{template_id}
```

### System Settings
```
GET /api/admin/settings
PUT /api/admin/settings
```

### Statistics
```
GET /api/admin/stats
```

## Database Schema

The system uses the following main tables:

1. `users` - User accounts and subscriptions
2. `email_templates` - Reusable email templates
3. `email_campaigns` - Campaign tracking and stats
4. `recipient_lists` - Mailing lists
5. `usage_stats` - User activity tracking
6. `system_settings` - Global configuration

## Security Considerations

1. Authentication
   - Use strong passwords
   - Implement rate limiting
   - Enable 2FA for admin access

2. Environment Security
   - Use secure environment variables
   - Rotate JWT secrets periodically
   - Keep service keys private

3. Data Protection
   - Enable SSL/TLS
   - Implement proper CORS policies
   - Regular security audits

4. Deployment
   - Use HTTPS only
   - Configure secure headers
   - Regular dependency updates

## Monitoring

1. Activity Logs
   - User actions are logged
   - System events are tracked
   - Error monitoring

2. Usage Statistics
   - Email sending metrics
   - User engagement data
   - System performance stats

## Troubleshooting

1. Database Connection Issues
   - Verify Supabase credentials
   - Check network connectivity
   - Validate table permissions

2. Authentication Problems
   - Confirm JWT secret
   - Check admin credentials
   - Verify token expiration

3. Email Sending Issues
   - Validate SMTP settings
   - Check rate limits
   - Monitor quota usage

## Support

For technical support or questions:
1. Check the error logs
2. Review documentation
3. Contact system administrator