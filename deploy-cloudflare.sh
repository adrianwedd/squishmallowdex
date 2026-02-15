#!/bin/bash
# Deploy Squishmallowdex to Cloudflare Pages

set -e

echo "🚀 Deploying Squishmallowdex to Cloudflare Pages..."

# Check if logged in
if ! wrangler whoami &> /dev/null; then
    echo "❌ Not logged in to Cloudflare"
    echo "Please run: wrangler login"
    echo "Or set: export CLOUDFLARE_API_TOKEN='your-token'"
    exit 1
fi

echo "✅ Authenticated with Cloudflare"

# Deploy to Pages
echo "📤 Deploying docs/ directory..."
wrangler pages deploy docs \
    --project-name=squishmallowdex \
    --branch=main \
    --commit-dirty=true

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your site is live at: https://squishmallowdex.pages.dev"
