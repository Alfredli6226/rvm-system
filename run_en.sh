#!/bin/bash

# RVM Customer Service System - Startup Script (English Version)

set -e

echo "========================================="
echo "🤖 RVM Customer Service System Starting"
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

# Check database
echo -e "${BLUE}[3/5] Checking database...${NC}"
if [ ! -f "data/rvm_service.db" ]; then
    echo -e "${YELLOW}Database not found, initializing...${NC}"
    python simple_init_db.py
else
    echo -e "${GREEN}✅ Database exists${NC}"
fi

# Start service
echo -e "${BLUE}[4/5] Starting Web service...${NC}"
echo -e "${YELLOW}Service will run in background...${NC}"

# Create log directory
mkdir -p logs

# Start Flask application (English version)
nohup python app_en.py > logs/app.log 2>&1 &
FLASK_PID=$!

# Wait for service to start
sleep 3

# Check service status
echo -e "${BLUE}[5/5] Checking service status...${NC}"
if curl -s http://localhost:5050/api/health > /dev/null; then
    echo -e "${GREEN}✅ Service started successfully!${NC}"
    echo ""
    echo "========================================="
    echo "🎉 RVM Customer Service System Ready"
    echo "========================================="
    echo ""
    echo "📊 Admin Interface: http://localhost:5050"
    echo "🔧 API Documentation: http://localhost:5050 (view page)"
    echo "📝 Log File: logs/app.log"
    echo "🔄 Process PID: $FLASK_PID"
    echo "🌐 Language: English"
    echo ""
    echo "🚀 Test Command:"
    echo "curl -X POST http://localhost:5050/api/auto-reply \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"phone_number\": \"+60123456789\", \"message\": \"RVM is full\"}'"
    echo ""
    echo "🛑 Stop Service: kill $FLASK_PID"
    echo "========================================="
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo "Check logs: tail -f logs/app.log"
    exit 1
fi

# Save PID to file
echo $FLASK_PID > .flask_pid

echo ""
echo -e "${YELLOW}Tip: Press Ctrl+C to exit, service will continue running in background${NC}"
echo "To stop service, run: ./stop_en.sh"

# Show logs
echo ""
echo -e "${BLUE}=== Last 10 lines of log ===${NC}"
tail -10 logs/app.log