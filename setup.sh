#!/bin/bash

echo "🧸 Squishmallowdex Setup"
echo "========================"
echo

# Check for Python 3
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found!"
    echo
    echo "Please install Python 3:"
    echo "  • Mac: brew install python3"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  • Windows: https://www.python.org/downloads/"
    exit 1
fi

echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --quiet requests beautifulsoup4 Pillow

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed!"
else
    echo "❌ Failed to install dependencies"
    echo "Try: pip3 install requests beautifulsoup4"
    exit 1
fi

echo
echo "🎉 Setup complete! Run the collector with:"
echo
echo "   python3 squishmallowdex.py --limit 50"
echo
