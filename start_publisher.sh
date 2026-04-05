#!/bin/bash

# Simple Social Media Publisher Startup Script

set -e

echo "========================================="
echo "📱 Simple Social Media Publisher"
echo "========================================="

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Checking configuration...${NC}"

# Check if tokens are configured
POWERNOW_CONFIGURED=false
LEE1_CONFIGURED=false

if [ -n "$POWERNOW_FB_TOKEN" ] && [ -n "$POWERNOW_IG_TOKEN" ]; then
    POWERNOW_CONFIGURED=true
fi

if [ -n "$LEE1_FB_TOKEN" ] && [ -n "$LEE1_IG_TOKEN" ]; then
    LEE1_CONFIGURED=true
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}📱 Simple Social Media Publisher${NC}"
echo -e "${GREEN}🏢 Brands: PowerNow Asia & Lee1 Healthcare${NC}"
echo -e "${GREEN}📊 Platforms: Facebook & Instagram${NC}"
echo -e "${GREEN}📅 Content: Daily automated posts${NC}"
echo -e "${GREEN}⏰ Schedule: 9:00 AM, 1:00 PM, 5:00 PM${NC}"
echo -e "${GREEN}=========================================${NC}"

echo -e "\n${BLUE}Configuration Status:${NC}"
if [ "$POWERNOW_CONFIGURED" = true ]; then
    echo -e "  PowerNow Asia: ${GREEN}✅ Configured${NC}"
else
    echo -e "  PowerNow Asia: ${YELLOW}⚠️ Not configured${NC}"
fi

if [ "$LEE1_CONFIGURED" = true ]; then
    echo -e "  Lee1 Healthcare: ${GREEN}✅ Configured${NC}"
else
    echo -e "  Lee1 Healthcare: ${YELLOW}⚠️ Not configured${NC}"
fi

if [ "$POWERNOW_CONFIGURED" = false ] && [ "$LEE1_CONFIGURED" = false ]; then
    echo -e "\n${YELLOW}⚠️ No social media tokens configured${NC}"
    echo -e "${YELLOW}   Running in preview mode only${NC}"
    echo -e "\n${BLUE}To configure, set environment variables:${NC}"
    echo -e "export POWERNOW_FB_TOKEN=\"your_token\""
    echo -e "export POWERNOW_IG_TOKEN=\"your_token\""
    echo -e "export LEE1_FB_TOKEN=\"your_token\""
    echo -e "export LEE1_IG_TOKEN=\"your_token\""
fi

echo -e "\n${BLUE}Available commands:${NC}"
echo -e "1. ${GREEN}Show status${NC}"
echo -e "   python simple_social_publisher.py --status"
echo -e "\n2. ${GREEN}Preview daily schedule${NC}"
echo -e "   python simple_social_publisher.py --schedule"
echo -e "\n3. ${GREEN}Add content to library${NC}"
echo -e "   python simple_social_publisher.py --add"
echo -e "\n4. ${GREEN}Post from library${NC}"
echo -e "   python simple_social_publisher.py --post"
echo -e "\n5. ${GREEN}Test content generation${NC}"
echo -e "   python simple_social_publisher.py"

echo -e "\n${BLUE}Example content generation:${NC}"
python simple_social_publisher.py --schedule

echo -e "\n${GREEN}✅ Publisher ready!${NC}"
echo -e "${YELLOW}Configure tokens to enable actual posting.${NC}"