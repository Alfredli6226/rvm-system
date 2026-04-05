#!/bin/bash

# RVM客户服务系统 - 启动脚本

set -e

echo "========================================="
echo "🤖 RVM客户服务系统启动"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python环境
echo -e "${BLUE}[1/5] 检查Python环境...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo -e "${BLUE}[2/5] 检查依赖...${NC}"
if [ ! -f "requirements_simple.txt" ]; then
    echo -e "${RED}错误: requirements_simple.txt 不存在${NC}"
    exit 1
fi

pip install -r requirements_simple.txt > /dev/null 2>&1
echo -e "${GREEN}✅ 依赖检查完成${NC}"

# 检查数据库
echo -e "${BLUE}[3/5] 检查数据库...${NC}"
if [ ! -f "data/rvm_service.db" ]; then
    echo -e "${YELLOW}数据库不存在，正在初始化...${NC}"
    python simple_init_db.py
else
    echo -e "${GREEN}✅ 数据库已存在${NC}"
fi

# 启动服务
echo -e "${BLUE}[4/5] 启动Web服务...${NC}"
echo -e "${YELLOW}服务将在后台运行...${NC}"

# 创建日志目录
mkdir -p logs

# 启动Flask应用
nohup python app.py > logs/app.log 2>&1 &
FLASK_PID=$!

# 等待服务启动
sleep 3

# 检查服务状态
echo -e "${BLUE}[5/5] 检查服务状态...${NC}"
if curl -s http://localhost:5050/api/health > /dev/null; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo ""
    echo "========================================="
    echo "🎉 RVM客户服务系统已就绪"
    echo "========================================="
    echo ""
    echo "📊 管理界面: http://localhost:5050"
    echo "🔧 API文档: http://localhost:5050 (查看页面)"
    echo "📝 日志文件: logs/app.log"
    echo "🔄 进程PID: $FLASK_PID"
    echo ""
    echo "🚀 测试命令:"
    echo "curl -X POST http://localhost:5050/api/auto-reply \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{\"phone_number\": \"+60123456789\", \"message\": \"RVM已满\"}'"
    echo ""
    echo "🛑 停止服务: kill $FLASK_PID"
    echo "========================================="
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看日志: tail -f logs/app.log"
    exit 1
fi

# 保存PID到文件
echo $FLASK_PID > .flask_pid

echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 退出，服务将继续在后台运行${NC}"
echo "要停止服务，运行: ./stop.sh"

# 显示日志
echo ""
echo -e "${BLUE}=== 最后10行日志 ===${NC}"
tail -10 logs/app.log