-- Reset: Drop all existing tables
DROP TABLE IF EXISTS usage_logs CASCADE;
DROP TABLE IF EXISTS email_templates CASCADE;
DROP TABLE IF EXISTS usage_stats CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;
DROP TABLE IF EXISTS email_campaigns CASCADE;
DROP TABLE IF EXISTS user_settings CASCADE;
DROP TABLE IF EXISTS recipient_lists CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table first (as it's referenced by other tables)
CREATE TABLE users (
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

-- Create recipient_lists table
CREATE TABLE recipient_lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    list_name VARCHAR(100) NOT NULL,
    recipients TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_settings table
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    settings TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create email_campaigns table
CREATE TABLE email_campaigns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    campaign_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
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

-- Create api_keys table
CREATE TABLE api_keys (
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

-- Create usage_stats table
CREATE TABLE usage_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    emails_sent INTEGER DEFAULT 0,
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Create email_templates table
CREATE TABLE email_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    template_name VARCHAR(100) NOT NULL,
    subject VARCHAR(255),
    body_text TEXT,
    body_html TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create usage_logs table
CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create system_settings table
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    default_daily_limit INTEGER DEFAULT 100,
    max_file_size INTEGER DEFAULT 10,
    smtp_host VARCHAR(255),
    smtp_port INTEGER DEFAULT 587,
    system_email VARCHAR(255),
    free_tier_templates BOOLEAN DEFAULT FALSE,
    free_tier_scheduling BOOLEAN DEFAULT FALSE,
    free_tier_api BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create all indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_subscription_end ON users(subscription_end);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_recipient_lists_user_id ON recipient_lists(user_id);
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX idx_email_campaigns_user_id ON email_campaigns(user_id);
CREATE INDEX idx_email_campaigns_status ON email_campaigns(status);
CREATE INDEX idx_email_templates_user_id ON email_templates(user_id);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);

-- Insert initial data
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
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2',
    'admin@emailsender.com',
    'admin',
    CURRENT_TIMESTAMP,
    '2030-12-31 23:59:59',
    true,
    true,
    999999
) ON CONFLICT (username) DO NOTHING;

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