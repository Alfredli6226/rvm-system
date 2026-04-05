#!/bin/bash

# RVM Customer Service System - Stop Script (English Version)

echo "========================================="
echo "🛑 RVM Customer Service System Stopping"
echo "========================================="

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check PID file
if [ -f ".flask_pid" ]; then
    PID=$(cat .flask_pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping process $PID...${NC}"
        kill $PID
        
        # Wait for process to stop
        sleep 2
        
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Force stopping process $PID...${NC}"
            kill -9 $PID
        fi
        
        echo -e "${GREEN}✅ Service stopped${NC}"
        rm -f .flask_pid
    else
        echo -e "${YELLOW}Process $PID does not exist${NC}"
        rm -f .flask_pid
    fi
else
    echo -e "${YELLOW}No running service found${NC}"
    
    # Try to find Flask processes
    FLASK_PIDS=$(ps aux | grep "python app_en.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$FLASK_PIDS" ]; then
        echo -e "${YELLOW}Found Flask processes: $FLASK_PIDS${NC}"
        for pid in $FLASK_PIDS; do
            echo "Stopping process $pid..."
            kill $pid
        done
        echo -e "${GREEN}✅ All Flask processes stopped${NC}"
    else
        echo -e "${GREEN}✅ No running services${NC}"
    fi
fi

echo ""
echo "========================================="
echo "Service Status: 🔴 Stopped"
echo "To restart: ./run_en.sh"
echo "========================================="