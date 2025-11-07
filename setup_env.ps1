# PowerShell script to add environment variables to Vercel
# Replace these with your actual values from Supabase

$SUPABASE_URL = "https://your-project-id.supabase.co"
$SUPABASE_ANON_KEY = "your-anon-key-here"
$SUPABASE_SERVICE_KEY = "your-service-key-here"
$JWT_SECRET = "7b92c44e7650d956f04bf50bc2e96bfce86f6c585199d45459aac369f8f28406"
$ADMIN_USERNAME = "admin"
$ADMIN_PASSWORD = "your-secure-admin-password"

Write-Host "🔧 Adding environment variables to Vercel..." -ForegroundColor Green

# Add each environment variable
Write-Host "Adding SUPABASE_URL..." -ForegroundColor Yellow
echo $SUPABASE_URL | vercel env add SUPABASE_URL production

Write-Host "Adding SUPABASE_ANON_KEY..." -ForegroundColor Yellow
echo $SUPABASE_ANON_KEY | vercel env add SUPABASE_ANON_KEY production

Write-Host "Adding SUPABASE_SERVICE_KEY..." -ForegroundColor Yellow
echo $SUPABASE_SERVICE_KEY | vercel env add SUPABASE_SERVICE_KEY production

Write-Host "Adding JWT_SECRET..." -ForegroundColor Yellow
echo $JWT_SECRET | vercel env add JWT_SECRET production

Write-Host "Adding ADMIN_USERNAME..." -ForegroundColor Yellow
echo $ADMIN_USERNAME | vercel env add ADMIN_USERNAME production

Write-Host "Adding ADMIN_PASSWORD..." -ForegroundColor Yellow
echo $ADMIN_PASSWORD | vercel env add ADMIN_PASSWORD production

Write-Host "✅ All environment variables added!" -ForegroundColor Green
Write-Host "🚀 Now run: vercel --prod to redeploy" -ForegroundColor Cyan