#!/bin/bash

# RVM客户服务系统安装脚本

set -e

echo "========================================="
echo "RVM客户服务系统 - 安装脚本"
echo "========================================="

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $python_version < "3.8" ]]; then
    echo "错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi
echo "✅ Python版本: $python_version"

# 检查pip
echo "检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "错误: pip3未安装"
    exit 1
fi
echo "✅ pip已安装"

# 创建虚拟环境
echo "创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "⚠️  虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 初始化数据库
echo "初始化数据库..."
cd database
python init_db.py
cd ..

# 创建必要的目录
echo "创建必要目录..."
mkdir -p logs
mkdir -p data/backups
mkdir -p web/static/uploads

echo "✅ 目录创建完成"

# 设置文件权限
echo "设置文件权限..."
chmod +x web/app.py
chmod +x core/auto_reply.py
chmod +x database/init_db.py
chmod +x scripts/*.sh 2>/dev/null || true

echo "✅ 文件权限设置完成"

# 创建环境变量文件
echo "创建环境变量文件..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# RVM客户服务系统环境变量

# 数据库配置
DATABASE_URL=sqlite:///database/customer_service.db

# Flask配置
FLASK_APP=web/app.py
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)

# WhatsApp配置
WHATSAPP_BUSINESS_NUMBER=+601110728228
WHATSAPP_WEBHOOK_URL=

# Telegram配置
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# 邮件配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=noreply@hmadigital.asia

# 备份配置
BACKUP_ENABLED=true
BACKUP_DIR=data/backups
BACKUP_RETENTION_DAYS=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/customer_service.log
EOF
    echo "✅ 环境变量文件创建完成"
else
    echo "⚠️  环境变量文件已存在，跳过创建"
fi

echo ""
echo "========================================="
echo "🎉 安装完成！"
echo "========================================="
echo ""
echo "下一步操作："
echo ""
echo "1. 启动系统："
echo "   source venv/bin/activate"
echo "   python web/app.py"
echo ""
echo "2. 访问系统："
echo "   打开浏览器访问 http://localhost:5000"
echo ""
echo "3. 登录账号："
echo "   • 管理员: admin / admin123"
echo "   • 客服: agent1 / agent123"
echo ""
echo "4. 配置环境变量："
echo "   编辑 .env 文件配置邮件、Telegram等"
echo ""
echo "5. 生产环境部署："
echo "   请参考 README.md 中的部署指南"
echo ""
echo "========================================="