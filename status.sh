#!/bin/bash

# RVM客户服务系统 - 状态检查脚本

echo "========================================="
echo "📊 RVM客户服务系统状态检查"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查服务是否运行
check_service() {
    echo -e "${BLUE}[1/4] 检查Web服务...${NC}"
    
    if curl -s http://localhost:5050/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Web服务运行正常${NC}"
        return 0
    else
        echo -e "${RED}❌ Web服务未运行${NC}"
        return 1
    fi
}

# 检查数据库
check_database() {
    echo -e "${BLUE}[2/4] 检查数据库...${NC}"
    
    if [ -f "data/rvm_service.db" ]; then
        DB_SIZE=$(du -h data/rvm_service.db | awk '{print $1}')
        echo -e "${GREEN}✅ 数据库文件存在 (大小: $DB_SIZE)${NC}"
        
        # 检查数据库连接
        if python -c "
import sqlite3
try:
    conn = sqlite3.connect('data/rvm_service.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM customers')
    count = cursor.fetchone()[0]
    print(f'客户数量: {count}')
    conn.close()
except Exception as e:
    print(f'数据库错误: {e}')
    exit(1)
" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 数据库连接正常${NC}"
        else
            echo -e "${RED}❌ 数据库连接失败${NC}"
        fi
    else
        echo -e "${RED}❌ 数据库文件不存在${NC}"
    fi
}

# 检查虚拟环境
check_venv() {
    echo -e "${BLUE}[3/4] 检查Python环境...${NC}"
    
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ 虚拟环境存在${NC}"
        
        # 检查关键包
        source venv/bin/activate
        if python -c "import flask, sqlite3" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 关键依赖已安装${NC}"
        else
            echo -e "${RED}❌ 缺少关键依赖${NC}"
        fi
        deactivate
    else
        echo -e "${RED}❌ 虚拟环境不存在${NC}"
    fi
}

# 获取系统信息
get_system_info() {
    echo -e "${BLUE}[4/4] 获取系统信息...${NC}"
    
    if check_service; then
        echo -e "${YELLOW}从API获取统计信息...${NC}"
        
        STATS=$(curl -s http://localhost:5050/api/stats)
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "📊 系统统计:"
            echo "-----------------------------------------"
            echo "$STATS" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['success']:
        stats = data['stats']
        print(f'总客户数: {stats[\"total_customers\"]}')
        print(f'总交互数: {stats[\"total_interactions\"]}')
        print(f'今日交互: {stats[\"today_interactions\"]}')
        print(f'待处理问题: {stats[\"open_issues\"]}')
        print(f'已解决问题: {stats[\"resolved_issues\"]}')
        
        print(f'\n📈 问题分布:')
        for item in data['issue_distribution']:
            print(f'  {item[\"issue_type\"]}: {item[\"count\"]}')
except:
    print('解析统计信息失败')
"
        fi
    fi
    
    # 显示进程信息
    echo ""
    echo "🖥️ 进程信息:"
    echo "-----------------------------------------"
    
    if [ -f ".flask_pid" ]; then
        PID=$(cat .flask_pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "进程ID: $PID"
            echo "运行时间: $(ps -p $PID -o etime= | xargs)"
            echo "内存使用: $(ps -p $PID -o rss= | awk '{print $1/1024 \" MB\"}')"
            echo "CPU使用: $(ps -p $PID -o %cpu=)%"
        fi
    fi
    
    # 显示日志信息
    echo ""
    echo "📝 日志信息:"
    echo "-----------------------------------------"
    if [ -f "logs/app.log" ]; then
        LOG_SIZE=$(du -h logs/app.log | awk '{print $1}')
        LOG_LINES=$(wc -l < logs/app.log)
        echo "日志文件: logs/app.log"
        echo "日志大小: $LOG_SIZE"
        echo "日志行数: $LOG_LINES"
        echo ""
        echo "最后5行日志:"
        tail -5 logs/app.log
    else
        echo "日志文件不存在"
    fi
}

# 执行检查
check_service
check_database
check_venv
get_system_info

echo ""
echo "========================================="
echo "🔧 管理命令:"
echo "  ./run.sh    - 启动服务"
echo "  ./stop.sh   - 停止服务"
echo "  ./status.sh - 查看状态"
echo "========================================="