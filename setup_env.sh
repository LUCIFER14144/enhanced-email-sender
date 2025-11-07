#!/bin/bash
# Script to add environment variables to Vercel
# Run this after setting up Supabase

# Replace these with your actual values
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_ANON_KEY="your-anon-key-here"
SUPABASE_SERVICE_KEY="your-service-key-here"
JWT_SECRET="7b92c44e7650d956f04bf50bc2e96bfce86f6c585199d45459aac369f8f28406"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="your-secure-admin-password"

echo "🔧 Adding environment variables to Vercel..."

# Add each environment variable
echo "Adding SUPABASE_URL..."
echo $SUPABASE_URL | vercel env add SUPABASE_URL production

echo "Adding SUPABASE_ANON_KEY..."
echo $SUPABASE_ANON_KEY | vercel env add SUPABASE_ANON_KEY production

echo "Adding SUPABASE_SERVICE_KEY..."
echo $SUPABASE_SERVICE_KEY | vercel env add SUPABASE_SERVICE_KEY production

echo "Adding JWT_SECRET..."
echo $JWT_SECRET | vercel env add JWT_SECRET production

echo "Adding ADMIN_USERNAME..."
echo $ADMIN_USERNAME | vercel env add ADMIN_USERNAME production

echo "Adding ADMIN_PASSWORD..."
echo $ADMIN_PASSWORD | vercel env add ADMIN_PASSWORD production

echo "✅ All environment variables added!"
echo "🚀 Now run: vercel --prod to redeploy"