#!/bin/bash

# RVM Customer Service System - Status Check Script (English Version)

echo "========================================="
echo "📊 RVM Customer Service System Status Check"
echo "========================================="

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if service is running
check_service() {
    echo -e "${BLUE}[1/4] Checking Web service...${NC}"
    
    if curl -s http://localhost:5050/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Web service running normally${NC}"
        return 0
    else
        echo -e "${RED}❌ Web service not running${NC}"
        return 1
    fi
}

# Check database
check_database() {
    echo -e "${BLUE}[2/4] Checking database...${NC}"
    
    if [ -f "data/rvm_service.db" ]; then
        DB_SIZE=$(du -h data/rvm_service.db | awk '{print $1}')
        echo -e "${GREEN}✅ Database file exists (size: $DB_SIZE)${NC}"
        
        # Check database connection
        if python -c "
import sqlite3
try:
    conn = sqlite3.connect('data/rvm_service.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM customers')
    count = cursor.fetchone()[0]
    print(f'Customer count: {count}')
    conn.close()
except Exception as e:
    print(f'Database error: {e}')
    exit(1)
" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Database connection normal${NC}"
        else
            echo -e "${RED}❌ Database connection failed${NC}"
        fi
    else
        echo -e "${RED}❌ Database file not found${NC}"
    fi
}

# Check virtual environment
check_venv() {
    echo -e "${BLUE}[3/4] Checking Python environment...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Virtual environment exists${NC}"
        
        # Check key packages
        source venv/bin/activate
        if python -c "import flask, sqlite3" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Key dependencies installed${NC}"
        else
            echo -e "${RED}❌ Missing key dependencies${NC}"
        fi
        deactivate
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
    fi
}

# Get system information
get_system_info() {
    echo -e "${BLUE}[4/4] Getting system information...${NC}"
    
    if check_service; then
        echo -e "${YELLOW}Getting statistics from API...${NC}"
        
        STATS=$(curl -s http://localhost:5050/api/stats)
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "📊 System Statistics:"
            echo "-----------------------------------------"
            echo "$STATS" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['success']:
        stats = data['stats']
        print(f'Total Customers: {stats[\"total_customers\"]}')
        print(f'Total Interactions: {stats[\"total_interactions\"]}')
        print(f\"Today's Interactions: {stats[\"today_interactions\"]}\")
        print(f'Open Issues: {stats[\"open_issues\"]}')
        print(f'Resolved Issues: {stats[\"resolved_issues\"]}')
        
        print(f'\n📈 Issue Distribution:')
        for item in data['issue_distribution']:
            print(f'  {item[\"issue_type\"]}: {item[\"count\"]}')
except:
    print('Failed to parse statistics')
"
        fi
    fi
    
    # Show process information
    echo ""
    echo "🖥️ Process Information:"
    echo "-----------------------------------------"
    
    if [ -f ".flask_pid" ]; then
        PID=$(cat .flask_pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "Process ID: $PID"
            echo "Uptime: $(ps -p $PID -o etime= | xargs)"
            echo "Memory Usage: $(ps -p $PID -o rss= | awk '{print $1/1024 \" MB\"}')"
            echo "CPU Usage: $(ps -p $PID -o %cpu=)%"
        fi
    fi
    
    # Show log information
    echo ""
    echo "📝 Log Information:"
    echo "-----------------------------------------"
    if [ -f "logs/app.log" ]; then
        LOG_SIZE=$(du -h logs/app.log | awk '{print $1}')
        LOG_LINES=$(wc -l < logs/app.log)
        echo "Log File: logs/app.log"
        echo "Log Size: $LOG_SIZE"
        echo "Log Lines: $LOG_LINES"
        echo ""
        echo "Last 5 lines of log:"
        tail -5 logs/app.log
    else
        echo "Log file not found"
    fi
}

# Execute checks
check_service
check_database
check_venv
get_system_info

echo ""
echo "========================================="
echo "🔧 Management Commands:"
echo "  ./run_en.sh    - Start service"
echo "  ./stop_en.sh   - Stop service"
echo "  ./status_en.sh - Check status"
echo "========================================="