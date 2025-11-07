-- Enhanced Email Sender Database Schema
-- Run this in your PostgreSQL/Supabase database

-- Users table with enhanced subscription management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    total_emails_sent INTEGER DEFAULT 0,
    daily_email_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recipient lists for each user
CREATE TABLE IF NOT EXISTS recipient_lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    list_name VARCHAR(100) NOT NULL,
    recipients TEXT NOT NULL, -- JSON array of email addresses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User settings storage
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    settings TEXT NOT NULL, -- JSON object
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Email campaigns table with enhanced features
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    recipients VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- draft, scheduled, sending, completed, failed, paused
    total_recipients INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    schedule_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email campaigns tracking with enhanced analytics
CREATE TABLE IF NOT EXISTS email_campaigns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    campaign_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sending, completed, failed, paused
    total_emails INTEGER DEFAULT 0,
    sent_emails INTEGER DEFAULT 0,
    successful_sends INTEGER DEFAULT 0,
    failed_sends INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    template_id INTEGER,
    settings JSONB DEFAULT '{}'::jsonb
);

-- API keys for desktop app authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    description VARCHAR(200),
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    UNIQUE(key_hash)
);

-- Usage statistics tracking
CREATE TABLE IF NOT EXISTS usage_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Email templates with versioning
CREATE TABLE IF NOT EXISTS email_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    template_name VARCHAR(100) NOT NULL,
    subject VARCHAR(255),
    body_text TEXT,
    body_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage logs for monitoring
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- login, email_sent, recipient_upload, etc.
    details TEXT, -- JSON object with additional info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_subscription_end ON users(subscription_end);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_recipient_lists_user_id ON recipient_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_user_id ON email_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_status ON email_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_email_templates_user_id ON email_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);

-- Insert default admin user (change password in production!)
INSERT INTO users (
    username, 
    hashed_password, 
    email, 
    subscription_tier, 
    subscription_start,
    subscription_end, 
    is_active,
    is_admin,
    daily_email_limit
) VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2', -- password: admin123
    'admin@emailsender.com',
    'admin',
    CURRENT_TIMESTAMP,
    '2030-12-31 23:59:59',
    true,
    true,
    999999
) ON CONFLICT (username) DO NOTHING;

-- Sample free user (password: demo123)
INSERT INTO users (
    username, 
    hashed_password, 
    email, 
    subscription_tier,
    subscription_start,
    subscription_end,
    is_active,
    is_admin,
    daily_email_limit
) VALUES (
    'demo',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2',
    'demo@example.com',
    'free',
    CURRENT_TIMESTAMP,
    '2025-12-06 23:59:59',
    true,
    false,
    100
) ON CONFLICT (username) DO NOTHING;
