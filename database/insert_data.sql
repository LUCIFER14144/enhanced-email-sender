-- Insert initial data after tables and indexes are created
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