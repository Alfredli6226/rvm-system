#!/bin/bash

# Social Media Manager Startup Script

set -e

echo "========================================="
echo "📱 Social Media Manager Starting"
echo "========================================="

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python environment
echo -e "${BLUE}[1/5] Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found, using system Python${NC}"
else
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
fi

# Check dependencies
echo -e "${BLUE}[2/5] Checking dependencies...${NC}"
pip install requests > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies checked${NC}"

# Check Facebook/Instagram configuration
echo -e "${BLUE}[3/5] Checking social media configuration...${NC}"

# Check PowerNow Asia configuration
POWERNOW_CONFIGURED=false
if [ -n "$POWERNOW_FB_TOKEN" ] && [ -n "$POWERNOW_IG_TOKEN" ]; then
    echo -e "${GREEN}✅ PowerNow Asia tokens configured${NC}"
    POWERNOW_CONFIGURED=true
else
    echo -e "${YELLOW}⚠️ PowerNow Asia tokens not configured${NC}"
fi

# Check Lee1 Healthcare configuration
LEE1_CONFIGURED=false
if [ -n "$LEE1_FB_TOKEN" ] && [ -n "$LEE1_IG_TOKEN" ]; then
    echo -e "${GREEN}✅ Lee1 Healthcare tokens configured${NC}"
    LEE1_CONFIGURED=true
else
    echo -e "${YELLOW}⚠️ Lee1 Healthcare tokens not configured${NC}"
fi

if [ "$POWERNOW_CONFIGURED" = false ] && [ "$LEE1_CONFIGURED" = false ]; then
    echo -e "${YELLOW}⚠️ No social media tokens configured${NC}"
    echo -e "${YELLOW}   Running in test mode only${NC}"
    echo -e "${YELLOW}   To configure, set environment variables:${NC}"
    echo -e "${YELLOW}   export POWERNOW_FB_TOKEN=\"your_token\"${NC}"
    echo -e "${YELLOW}   export LEE1_FB_TOKEN=\"your_token\"${NC}"
    echo -e "${YELLOW}   See SOCIAL_MEDIA_SETUP.md for details${NC}"
fi

# Check if other systems are running
echo -e "${BLUE}[4/5] Checking other systems...${NC}"
if curl -s http://localhost:5060/api/rvm/health > /dev/null; then
    echo -e "${GREEN}✅ RVM Management System is running${NC}"
else
    echo -e "${YELLOW}⚠️ RVM Management System is not running${NC}"
fi

if curl -s http://localhost:5050/api/health > /dev/null; then
    echo -e "${GREEN}✅ Customer Service System is running${NC}"
else
    echo -e "${YELLOW}⚠️ Customer Service System is not running${NC}"
fi

# Start social media manager
echo -e "${BLUE}[5/5] Starting Social Media Manager...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}📱 Social Media Manager Started${NC}"
echo -e "${GREEN}🏢 Monitoring: PowerNow Asia & Lee1 Healthcare${NC}"
echo -e "${GREEN}📊 Platforms: Facebook & Instagram${NC}"
echo -e "${GREEN}⏰ Check interval: Every 5 minutes${NC}"
echo -e "${GREEN}🤖 Auto-reply: Enabled${NC}"
echo -e "${GREEN}🛑 Stop with: Ctrl+C${NC}"
echo -e "${GREEN}=========================================${NC}"

# Run test first
echo -e "${BLUE}Running test...${NC}"
python social_media_manager.py --test

echo -e "${BLUE}Starting monitor...${NC}"
python social_media_manager.py