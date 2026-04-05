#!/bin/bash

# Simple Social Media Publisher Startup Script
# Updated for Business Definitions (2026-04-05)

echo "=========================================="
echo "📱 SIMPLE SOCIAL MEDIA PUBLISHER"
echo "=========================================="
echo "PowerNow Asia: Shared Power Bank Rental"
echo "Lee1 Healthcare: TCM Acupuncture & Wellness"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in virtual environment. Installing dependencies globally..."
    
    # Install required packages
    echo "📦 Installing dependencies..."
    pip3 install --user requests
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Check content library
if [ ! -f "content/content_library.json" ]; then
    echo "📝 Creating content library..."
    mkdir -p content
    cat > content/content_library.json << 'EOF'
{
  "powernow_asia": [],
  "lee1_healthcare": []
}
EOF
fi

# Check environment variables
echo "🔍 Checking environment variables..."

if [ -z "$POWERNOW_FB_TOKEN" ] && [ -z "$LEE1_FB_TOKEN" ]; then
    echo "⚠️  No Facebook tokens found. Running in simulation mode."
    echo "   To enable actual posting, set:"
    echo "   export POWERNOW_FB_TOKEN='your_token'"
    echo "   export LEE1_FB_TOKEN='your_token'"
    echo "   export POWERNOW_FB_PAGE_ID='your_page_id'"
    echo "   export LEE1_FB_PAGE_ID='your_page_id'"
    echo "   export POWERNOW_IG_TOKEN='your_token'"
    echo "   export LEE1_IG_TOKEN='your_token'"
    echo "   export POWERNOW_IG_ID='your_ig_id'"
    echo "   export LEE1_IG_ID='your_ig_id'"
    echo ""
    echo "📝 Running in SIMULATION MODE - No actual posts will be made"
fi

# Run the publisher
echo ""
echo "🚀 Starting Social Media Publisher..."
echo "=========================================="

python3 simple_social_publisher.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Publisher completed successfully!"
else
    echo ""
    echo "❌ Publisher encountered an error"
    exit 1
fi

echo ""
echo "📋 NEXT STEPS:"
echo "1. Review the simulation results above"
echo "2. Add more content to content/content_library.json"
echo "3. Get Facebook/Instagram tokens for actual posting"
echo "4. Set environment variables and run again"
echo ""
echo "📞 For help: Check SOCIAL_MEDIA_SETUP.md"
echo "=========================================="