# PowerShell script to set up development database
# Run this script to initialize the development database environment

Write-Host "Setting up development database environment..." -ForegroundColor Green

# Load environment variables from .env.development
$envFile = ".env.development"
$envContent = Get-Content $envFile
$envVars = @{}
foreach ($line in $envContent) {
    if ($line -match '^([^#][^=]+)=(.+)$') {
        $envVars[$matches[1]] = $matches[2]
    }
}

# Check if PostgreSQL is installed
try {
    $pgVersion = psql --version
    Write-Host "PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install PostgreSQL and try again" -ForegroundColor Red
    exit 1
}

# Create development database
Write-Host "Creating development database..." -ForegroundColor Yellow
$createDB = @"
CREATE DATABASE $($envVars['POSTGRES_DB']);
CREATE USER $($envVars['POSTGRES_USER']) WITH PASSWORD '$($envVars['POSTGRES_PASSWORD'])';
GRANT ALL PRIVILEGES ON DATABASE $($envVars['POSTGRES_DB']) TO $($envVars['POSTGRES_USER']);
"@

try {
    $createDB | psql -U postgres
    Write-Host "Database created successfully" -ForegroundColor Green
} catch {
    Write-Host "Error creating database: $_" -ForegroundColor Red
    exit 1
}

# Initialize schema
Write-Host "Initializing database schema..." -ForegroundColor Yellow
try {
    psql -U $($envVars['POSTGRES_USER']) -d $($envVars['POSTGRES_DB']) -f "database/schema.sql"
    Write-Host "Schema initialized successfully" -ForegroundColor Green
} catch {
    Write-Host "Error initializing schema: $_" -ForegroundColor Red
    exit 1
}

# Create test data
Write-Host "Creating test data..." -ForegroundColor Yellow
$testData = @"
-- Insert test users with different subscription tiers
INSERT INTO users (username, hashed_password, email, subscription_tier, subscription_start, subscription_end, is_active, daily_email_limit)
VALUES
    ('test_basic', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2', 'basic@test.com', 'basic', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '30 days', true, 500),
    ('test_premium', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2', 'premium@test.com', 'premium', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '30 days', true, 2000),
    ('test_enterprise', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5DKHKz0Kz2', 'enterprise@test.com', 'enterprise', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '365 days', true, 10000)
ON CONFLICT (username) DO NOTHING;

-- Insert test email templates
INSERT INTO email_templates (user_id, template_name, subject, body_html)
SELECT 
    u.id,
    'Welcome Template',
    'Welcome to our service',
    '<h1>Welcome!</h1><p>Thank you for joining our service.</p>'
FROM users u
WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;

-- Insert test recipient lists
INSERT INTO recipient_lists (user_id, list_name, recipients)
SELECT 
    u.id,
    'Test List',
    '[{"email":"test1@example.com"},{"email":"test2@example.com"}]'
FROM users u
WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;

-- Insert test API keys
INSERT INTO api_keys (user_id, key_hash, description, expires_at)
SELECT 
    u.id,
    'test_api_key_hash',
    'Development Testing Key',
    CURRENT_TIMESTAMP + INTERVAL '365 days'
FROM users u
WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;
"@

try {
    $testData | psql -U $($envVars['POSTGRES_USER']) -d $($envVars['POSTGRES_DB'])
    Write-Host "Test data created successfully" -ForegroundColor Green
} catch {
    Write-Host "Error creating test data: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nDevelopment environment setup complete!" -ForegroundColor Green
Write-Host "You can now start the application with:" -ForegroundColor Yellow
Write-Host "uvicorn api.main_production:app --reload --env-file .env.development" -ForegroundColor Cyan