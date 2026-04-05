#!/bin/bash

# RVM Management System - Startup Script

set -e

echo "========================================="
echo "🏢 RVM Management System Starting"
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
    echo -e "${YELLOW}Virtual environment not found, creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo -e "${BLUE}[2/5] Checking dependencies...${NC}"
if [ ! -f "requirements_simple.txt" ]; then
    echo -e "${RED}Error: requirements_simple.txt not found${NC}"
    exit 1
fi

pip install -r requirements_simple.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies checked${NC}"

# Initialize RVM management database
echo -e "${BLUE}[3/5] Initializing RVM management database...${NC}"
if [ ! -f "data/rvm_management.db" ]; then
    echo -e "${YELLOW}RVM management database not found, initializing...${NC}"
    python init_rvm_database.py
    echo -e "${GREEN}✅ RVM management database initialized${NC}"
else
    echo -e "${GREEN}✅ RVM management database already exists${NC}"
fi

# Check if customer service system is running
echo -e "${BLUE}[4/5] Checking customer service system...${NC}"
if curl -s http://localhost:5050/api/health > /dev/null; then
    echo -e "${GREEN}✅ Customer service system is running${NC}"
else
    echo -e "${YELLOW}⚠️ Customer service system is not running${NC}"
    echo -e "${YELLOW}   Starting customer service system...${NC}"
    ./run_en.sh &
    sleep 3
fi

# Start RVM management system
echo -e "${BLUE}[5/5] Starting RVM management system...${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}🚀 RVM Management System is starting on port 5060${NC}"
echo -e "${GREEN}📊 Dashboard: http://localhost:5060/rvm-dashboard${NC}"
echo -e "${GREEN}📋 API Health: http://localhost:5060/api/rvm/health${NC}"
echo -e "${GREEN}=========================================${NC}"

# Run the application
python rvm_management.py