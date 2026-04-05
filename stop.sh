#!/bin/bash

# RVM客户服务系统 - 停止脚本

echo "========================================="
echo "🛑 RVM客户服务系统停止"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查PID文件
if [ -f ".flask_pid" ]; then
    PID=$(cat .flask_pid)
    
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${YELLOW}停止进程 $PID...${NC}"
        kill $PID
        
        # 等待进程停止
        sleep 2
        
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${YELLOW}强制停止进程 $PID...${NC}"
            kill -9 $PID
        fi
        
        echo -e "${GREEN}✅ 服务已停止${NC}"
        rm -f .flask_pid
    else
        echo -e "${YELLOW}进程 $PID 不存在${NC}"
        rm -f .flask_pid
    fi
else
    echo -e "${YELLOW}未找到运行中的服务${NC}"
    
    # 尝试查找Flask进程
    FLASK_PIDS=$(ps aux | grep "python app.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$FLASK_PIDS" ]; then
        echo -e "${YELLOW}找到Flask进程: $FLASK_PIDS${NC}"
        for pid in $FLASK_PIDS; do
            echo "停止进程 $pid..."
            kill $pid
        done
        echo -e "${GREEN}✅ 所有Flask进程已停止${NC}"
    else
        echo -e "${GREEN}✅ 没有运行中的服务${NC}"
    fi
fi

echo ""
echo "========================================="
echo "服务状态: 🔴 已停止"
echo "要重新启动: ./run.sh"
echo "========================================="