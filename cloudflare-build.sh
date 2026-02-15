#!/bin/bash
# Cloudflare Pages Build Script

set -e  # Exit on error

echo "🚀 Starting Cloudflare Pages build..."

# Check Python version
echo "📦 Python version:"
python3 --version

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements-test.txt

# Generate the collection
echo "🎨 Generating Squishmallowdex collection..."
python3 squishmallowdex.py

# Deploy to docs folder
echo "📂 Deploying to /docs..."
python3 deploy.py

# Verify deployment
echo "✅ Verifying deployment..."
if [ -f "docs/index.html" ] && [ -f "docs/squishmallowdex.html" ]; then
    echo "✅ Build successful!"
    echo "📊 Build stats:"
    echo "   - HTML files: $(find docs -name '*.html' | wc -l)"
    echo "   - Images: $(find docs/squish_images -type f 2>/dev/null | wc -l || echo 0)"
    echo "   - Total size: $(du -sh docs | cut -f1)"
else
    echo "❌ Build failed - missing required files"
    exit 1
fi

echo "🎉 Cloudflare build complete!"
