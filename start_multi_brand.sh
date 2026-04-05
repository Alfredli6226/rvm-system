#!/bin/bash

# Multi-Brand Social Media Publisher Startup Script
# Supports 4 brands: MyGreenPlus, ShiftByAlf, PowerNow Asia, Lee1 Healthcare

echo "=========================================="
echo "📱 MULTI-BRAND SOCIAL MEDIA PUBLISHER"
echo "=========================================="
echo "Supports 4 brands:"
echo "1. MyGreenPlus - Smart RVM Recycling"
echo "2. ShiftByAlf - [Business definition pending]"
echo "3. PowerNow Asia - Power Bank Rental"
echo "4. Lee1 Healthcare - TCM Acupuncture"
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
  "mygreenplus": [],
  "shiftbyalf": [],
  "powernow_asia": [],
  "lee1_healthcare": []
}
EOF
fi

# Check environment variables
echo "🔍 Checking environment variables..."

# List all required environment variables
required_vars=(
    "MYGREENPLUS_FB_TOKEN"
    "MYGREENPLUS_FB_PAGE_ID"
    "MYGREENPLUS_IG_TOKEN"
    "MYGREENPLUS_IG_ID"
    "SHIFTBVALF_FB_TOKEN"
    "SHIFTBVALF_FB_PAGE_ID"
    "SHIFTBVALF_IG_TOKEN"
    "SHIFTBVALF_IG_ID"
    "POWERNOW_FB_TOKEN"
    "POWERNOW_FB_PAGE_ID"
    "POWERNOW_IG_TOKEN"
    "POWERNOW_IG_ID"
    "LEE1_FB_TOKEN"
    "LEE1_FB_PAGE_ID"
    "LEE1_IG_TOKEN"
    "LEE1_IG_ID"
)

missing_vars=0
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars=$((missing_vars + 1))
    fi
done

if [ $missing_vars -eq ${#required_vars[@]} ]; then
    echo "⚠️  No social media tokens found. Running in simulation mode."
    echo "   To enable actual posting, set environment variables."
    echo ""
    echo "📝 Running in SIMULATION MODE - No actual posts will be made"
elif [ $missing_vars -gt 0 ]; then
    echo "⚠️  Some tokens missing ($missing_vars/${#required_vars[@]}). Mixed mode."
    echo "   Brands with tokens will post, others will simulate."
else
    echo "✅ All tokens configured. Running in PRODUCTION MODE."
fi

# Run the test
echo ""
echo "🧪 Running multi-brand test..."
echo "=========================================="

python3 test_multi_brand.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Multi-brand test completed successfully!"
else
    echo ""
    echo "❌ Test encountered an error"
    exit 1
fi

echo ""
echo "📋 URGENT ACTIONS NEEDED:"
echo "1. Define ShiftByAlf business (tell me what it is)"
echo "2. Get Facebook/Instagram tokens for brands"
echo "3. Add more content to content library"
echo ""
echo "🚀 Once ShiftByAlf is defined, I'll create proper content!"
echo "=========================================="