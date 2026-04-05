#!/bin/bash

# Telegram Alert Monitor Startup Script

set -e

echo "========================================="
echo "📱 Telegram Alert Monitor Starting"
echo "========================================="

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python environment
echo -e "${BLUE}[1/4] Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found, using system Python${NC}"
else
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
fi

# Check Telegram configuration
echo -e "${BLUE}[2/4] Checking Telegram configuration...${NC}"
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️ TELEGRAM_BOT_TOKEN not set${NC}"
    echo -e "${YELLOW}   Running in test mode (alerts printed locally)${NC}"
    echo -e "${YELLOW}   To enable Telegram alerts:${NC}"
    echo -e "${YELLOW}   1. Create bot with @BotFather${NC}"
    echo -e "${YELLOW}   2. Get bot token${NC}"
    echo -e "${YELLOW}   3. Set environment variable:${NC}"
    echo -e "${YELLOW}      export TELEGRAM_BOT_TOKEN='your_token_here'${NC}"
else
    echo -e "${GREEN}✅ Telegram bot token configured${NC}"
fi

# Check if RVM systems are running
echo -e "${BLUE}[3/4] Checking RVM systems...${NC}"
if curl -s http://localhost:5060/api/rvm/health > /dev/null; then
    echo -e "${GREEN}✅ RVM Management System is running${NC}"
else
    echo -e "${RED}❌ RVM Management System is not running${NC}"
    echo -e "${YELLOW}   Starting RVM Management System...${NC}"
    ./run_rvm_management.sh &
    sleep 5
fi

if curl -s http://localhost:5050/api/health > /dev/null; then
    echo -e "${GREEN}✅ Customer Service System is running${NC}"
else
    echo -e "${RED}❌ Customer Service System is not running${NC}"
    echo -e "${YELLOW}   Starting Customer Service System...${NC}"
    ./run_en.sh &
    sleep 5
fi

# Start Telegram alert monitor
echo -e "${BLUE}[4/4] Starting Telegram Alert Monitor...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}📱 Telegram Alert Monitor Started${NC}"
echo -e "${GREEN}📊 Monitoring: 6 RVM locations${NC}"
echo -e "${GREEN}👥 Monitoring: Customer service${NC}"
echo -e "${GREEN}⏰ Check interval: Every 5 minutes${NC}"
echo -e "${GREEN}📅 Daily summary: 9:00 AM${NC}"
echo -e "${GREEN}🛑 Stop with: Ctrl+C${NC}"
echo -e "${GREEN}=========================================${NC}"

# Run the monitor
python telegram_alerts.py