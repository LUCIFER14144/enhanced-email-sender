-- Enhanced Email Sender Database Schema
-- Run this in your PostgreSQL/Supabase database

-- Users table with subscription management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    subscription_type VARCHAR(50) DEFAULT 'free',
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    total_emails_sent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- Email campaigns tracking
CREATE TABLE IF NOT EXISTS email_campaigns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    campaign_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sending, completed, failed
    total_emails INTEGER DEFAULT 0,
    sent_emails INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Email templates (optional)
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
CREATE INDEX IF NOT EXISTS idx_users_expires_at ON users(expires_at);
CREATE INDEX IF NOT EXISTS idx_recipient_lists_user_id ON recipient_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_user_id ON email_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_email_campaigns_status ON email_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_email_templates_user_id ON email_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);

-- Insert default admin user (change password in production!)
INSERT INTO users (username, hashed_password, email, subscription_type, expires_at, is_active)
VALUES (
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2', -- password: admin123
    'admin@emailsender.com',
    'admin',
    '2030-12-31 23:59:59',
    true
) ON CONFLICT (username) DO NOTHING;

-- Sample free user (password: demo123)
INSERT INTO users (username, hashed_password, email, subscription_type, expires_at, is_active)
VALUES (
    'demo',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2',
    'demo@example.com',
    'free',
    '2025-12-06 23:59:59',
    true
) ON CONFLICT (username) DO NOTHING;
