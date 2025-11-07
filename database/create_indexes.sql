-- Create basic indexes first
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Create subscription-related indexes
CREATE INDEX idx_users_subscription_end ON users(subscription_end);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);

-- Create foreign key indexes
CREATE INDEX idx_recipient_lists_user_id ON recipient_lists(user_id);
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX idx_email_campaigns_user_id ON email_campaigns(user_id);
CREATE INDEX idx_email_templates_user_id ON email_templates(user_id);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);

-- Create additional indexes
CREATE INDEX idx_email_campaigns_status ON email_campaigns(status);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);