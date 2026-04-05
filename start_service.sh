#!/bin/bash

# RVM客户服务系统启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示横幅
show_banner() {
    echo "=================================================="
    echo "    RVM客户服务系统 v1.0.0"
    echo "    HMA Digital Sdn Bhd - MyGreenPlus"
    echo "=================================================="
    echo ""
}

# 检查系统状态
check_system() {
    log_info "检查系统状态..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        return 1
    fi
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_warning "虚拟环境不存在，请先运行 setup.sh"
        return 1
    fi
    
    # 检查数据库
    if [ ! -f "database/customer_service.db" ]; then
        log_warning "数据库不存在，请先运行 setup.sh"
        return 1
    fi
    
    log_success "系统检查通过"
    return 0
}

# 激活虚拟环境
activate_venv() {
    log_info "激活虚拟环境..."
    source venv/bin/activate
    
    if [ $? -eq 0 ]; then
        log_success "虚拟环境激活成功"
    else
        log_error "虚拟环境激活失败"
        return 1
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        log_warning "端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 启动Web服务
start_web_service() {
    local port=${1:-5000}
    local host=${2:-0.0.0.0}
    
    log_info "启动Web服务 (端口: $port, 主机: $host)..."
    
    # 检查端口
    if ! check_port $port; then
        log_error "无法启动Web服务，端口 $port 已被占用"
        return 1
    fi
    
    # 设置环境变量
    export FLASK_APP=web/app.py
    export FLASK_ENV=development
    
    # 加载.env文件
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
    fi
    
    # 启动服务
    nohup python -m flask run --host=$host --port=$port > logs/web_service.log 2>&1 &
    WEB_PID=$!
    
    sleep 2
    
    # 检查是否启动成功
    if ps -p $WEB_PID > /dev/null; then
        log_success "Web服务启动成功 (PID: $WEB_PID)"
        echo $WEB_PID > .web_pid
        return 0
    else
        log_error "Web服务启动失败"
        return 1
    fi
}

# 启动自动回复服务
start_auto_reply_service() {
    log_info "启动自动回复服务..."
    
    # 启动自动回复监控
    nohup python core/auto_reply_monitor.py > logs/auto_reply.log 2>&1 &
    AUTO_REPLY_PID=$!
    
    sleep 1
    
    if ps -p $AUTO_REPLY_PID > /dev/null; then
        log_success "自动回复服务启动成功 (PID: $AUTO_REPLY_PID)"
        echo $AUTO_REPLY_PID > .auto_reply_pid
        return 0
    else
        log_error "自动回复服务启动失败"
        return 1
    fi
}

# 启动定时任务
start_cron_jobs() {
    log_info "启动定时任务..."
    
    # 启动报告生成任务
    nohup python scripts/generate_reports.py > logs/reports.log 2>&1 &
    REPORTS_PID=$!
    
    sleep 1
    
    if ps -p $REPORTS_PID > /dev/null; then
        log_success "定时任务启动成功 (PID: $REPORTS_PID)"
        echo $REPORTS_PID > .reports_pid
        return 0
    else
        log_error "定时任务启动失败"
        return 1
    fi
}

# 显示服务状态
show_status() {
    echo ""
    echo "=================================================="
    echo "    服务状态"
    echo "=================================================="
    
    # Web服务状态
    if [ -f ".web_pid" ]; then
        WEB_PID=$(cat .web_pid)
        if ps -p $WEB_PID > /dev/null; then
            echo -e "Web服务: ${GREEN}运行中${NC} (PID: $WEB_PID)"
        else
            echo -e "Web服务: ${RED}已停止${NC}"
        fi
    else
        echo -e "Web服务: ${YELLOW}未启动${NC}"
    fi
    
    # 自动回复服务状态
    if [ -f ".auto_reply_pid" ]; then
        AUTO_REPLY_PID=$(cat .auto_reply_pid)
        if ps -p $AUTO_REPLY_PID > /dev/null; then
            echo -e "自动回复: ${GREEN}运行中${NC} (PID: $AUTO_REPLY_PID)"
        else
            echo -e "自动回复: ${RED}已停止${NC}"
        fi
    else
        echo -e "自动回复: ${YELLOW}未启动${NC}"
    fi
    
    # 定时任务状态
    if [ -f ".reports_pid" ]; then
        REPORTS_PID=$(cat .reports_pid)
        if ps -p $REPORTS_PID > /dev/null; then
            echo -e "定时任务: ${GREEN}运行中${NC} (PID: $REPORTS_PID)"
        else
            echo -e "定时任务: ${RED}已停止${NC}"
        fi
    else
        echo -e "定时任务: ${YELLOW}未启动${NC}"
    fi
    
    echo ""
    echo "=================================================="
    echo "    访问信息"
    echo "=================================================="
    echo "Web界面: http://localhost:5000"
    echo "API文档: http://localhost:5000/api/docs"
    echo ""
    echo "登录账号:"
    echo "  • 管理员: admin / admin123"
    echo "  • 客服: agent1 / agent123"
    echo ""
    echo "日志文件:"
    echo "  • Web服务: logs/web_service.log"
    echo "  • 自动回复: logs/auto_reply.log"
    echo "  • 定时任务: logs/reports.log"
    echo ""
}

# 停止服务
stop_service() {
    log_info "停止服务..."
    
    # 停止Web服务
    if [ -f ".web_pid" ]; then
        WEB_PID=$(cat .web_pid)
        if ps -p $WEB_PID > /dev/null; then
            kill $WEB_PID
            log_success "Web服务已停止"
        fi
        rm -f .web_pid
    fi
    
    # 停止自动回复服务
    if [ -f ".auto_reply_pid" ]; then
        AUTO_REPLY_PID=$(cat .auto_reply_pid)
        if ps -p $AUTO_REPLY_PID > /dev/null; then
            kill $AUTO_REPLY_PID
            log_success "自动回复服务已停止"
        fi
        rm -f .auto_reply_pid
    fi
    
    # 停止定时任务
    if [ -f ".reports_pid" ]; then
        REPORTS_PID=$(cat .reports_pid)
        if ps -p $REPORTS_PID > /dev/null; then
            kill $REPORTS_PID
            log_success "定时任务已停止"
        fi
        rm -f .reports_pid
    fi
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    stop_service
    sleep 2
    start_all_services
}

# 启动所有服务
start_all_services() {
    show_banner
    
    # 检查系统
    if ! check_system; then
        log_error "系统检查失败，无法启动服务"
        exit 1
    fi
    
    # 激活虚拟环境
    if ! activate_venv; then
        exit 1
    fi
    
    # 启动服务
    start_web_service
    start_auto_reply_service
    start_cron_jobs
    
    # 显示状态
    show_status
    
    log_success "所有服务启动完成！"
}

# 主函数
main() {
    local command=${1:-start}
    
    case $command in
        start)
            start_all_services
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            echo "用法: $0 [command]"
            echo ""
            echo "命令:"
            echo "  start     启动所有服务"
            echo "  stop      停止所有服务"
            echo "  restart   重启所有服务"
            echo "  status    显示服务状态"
            echo "  help      显示帮助信息"
            echo ""
            ;;
        *)
            echo "未知命令: $command"
            echo "使用 '$0 help' 查看可用命令"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"