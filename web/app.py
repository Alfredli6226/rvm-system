#!/usr/bin/env python3
# RVM客户服务系统Web界面

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import logging

from database.models import DatabaseManager, Interaction, InteractionType, Issue, IssueStatus
from core.auto_reply import AutoReplyEngine
from config.settings import BASE_DIR

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rvm-customer-service-secret-key-2026')
CORS(app)

# 初始化组件
db_manager = DatabaseManager()
auto_reply_engine = AutoReplyEngine(
    keywords_path=str(BASE_DIR / 'config' / 'keywords.json'),
    templates_path=str(BASE_DIR / 'config' / 'templates.json')
)

# 上下文处理器 - 使变量在所有模板中可用
@app.context_processor
def inject_globals():
    return {
        'now': datetime.now(),
        'app_name': 'RVM客户服务系统',
        'version': '1.0.0'
    }

# 路由定义
@app.route('/')
def index():
    """首页 - 仪表板"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # 获取统计数据
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        stats = {
            'total_interactions': db_manager.session.query(Interaction).filter(
                Interaction.timestamp.between(start_date, end_date)
            ).count(),
            'new_issues': db_manager.session.query(Issue).filter(
                Issue.created_at.between(start_date, end_date),
                Issue.status == IssueStatus.NEW
            ).count(),
            'pending_issues': db_manager.session.query(Issue).filter(
                Issue.status.in_([IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.PENDING])
            ).count(),
            'resolved_today': db_manager.session.query(Issue).filter(
                Issue.status == IssueStatus.RESOLVED,
                Issue.updated_at.between(start_date, end_date)
            ).count(),
        }
        
        # 获取最近交互
        recent_interactions = db_manager.session.query(Interaction).order_by(
            Interaction.timestamp.desc()
        ).limit(10).all()
        
        # 获取待处理问题
        pending_issues = db_manager.get_pending_issues(limit=10)
        
        return render_template('index.html', 
                             stats=stats,
                             recent_interactions=recent_interactions,
                             pending_issues=pending_issues)
        
    except Exception as e:
        logger.error(f"加载首页时出错: {e}")
        return render_template('error.html', error=str(e))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单验证（生产环境应使用密码哈希）
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('index'))
        elif username == 'agent1' and password == 'agent123':
            session['user_id'] = 2
            session['username'] = username
            session['role'] = 'agent'
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/customers')
def customers():
    """客户列表"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        customers = db_manager.session.query(db_manager.Customer).order_by(
            db_manager.Customer.created_at.desc()
        ).all()
        
        return render_template('customers.html', customers=customers)
        
    except Exception as e:
        logger.error(f"加载客户列表时出错: {e}")
        return render_template('error.html', error=str(e))

@app.route('/interactions')
def interactions():
    """交互记录"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        page = int(request.args.get('page', 1))
        per_page = 20
        
        interactions = db_manager.session.query(Interaction).order_by(
            Interaction.timestamp.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()
        
        total = db_manager.session.query(Interaction).count()
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('interactions.html', 
                             interactions=interactions,
                             page=page,
                             total_pages=total_pages,
                             total=total)
        
    except Exception as e:
        logger.error(f"加载交互记录时出错: {e}")
        return render_template('error.html', error=str(e))

@app.route('/issues')
def issues():
    """问题跟踪"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        status_filter = request.args.get('status', 'all')
        
        query = db_manager.session.query(Issue)
        
        if status_filter != 'all':
            query = query.filter(Issue.status == IssueStatus(status_filter))
        
        issues = query.order_by(Issue.created_at.desc()).all()
        
        return render_template('issues.html', 
                             issues=issues,
                             status_filter=status_filter,
                             IssueStatus=IssueStatus)
        
    except Exception as e:
        logger.error(f"加载问题列表时出错: {e}")
        return render_template('error.html', error=str(e))

@app.route('/auto-reply')
def auto_reply_page():
    """自动回复页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('auto_reply.html')

@app.route('/api/auto-reply', methods=['POST'])
def api_auto_reply():
    """自动回复API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        customer_phone = data.get('customer_phone', '')
        
        if not message:
            return jsonify({'success': False, 'error': '消息不能为空'}), 400
        
        # 获取或创建客户
        customer = None
        if customer_phone:
            customer = db_manager.add_customer(phone_number=customer_phone)
            customer_info = {
                'customer_name': customer.name,
                'customer_phone': customer.phone_number
            }
        else:
            customer_info = {}
        
        # 处理消息
        result = auto_reply_engine.process_message(message, customer_info)
        
        if result['success']:
            # 记录交互
            if customer:
                db_manager.log_interaction(
                    customer_id=customer.id,
                    interaction_type=InteractionType.INCOMING,
                    message=message,
                    reply=result['reply'],
                    category=result['category'],
                    confidence_score=result['confidence'],
                    location=result.get('extracted_location')
                )
            
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"自动回复API出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/log-interaction', methods=['POST'])
def api_log_interaction():
    """记录交互API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    try:
        data = request.get_json()
        
        required_fields = ['customer_phone', 'message', 'reply']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必要字段: {field}'}), 400
        
        # 获取或创建客户
        customer = db_manager.add_customer(
            phone_number=data['customer_phone'],
            name=data.get('customer_name'),
            location=data.get('location')
        )
        
        # 记录交互
        interaction = db_manager.log_interaction(
            customer_id=customer.id,
            interaction_type=InteractionType.INCOMING,
            message=data['message'],
            reply=data['reply'],
            category=data.get('category'),
            confidence_score=data.get('confidence_score'),
            location=data.get('location')
        )
        
        return jsonify({
            'success': True,
            'interaction_id': interaction.id,
            'customer_id': customer.id
        })
        
    except Exception as e:
        logger.error(f"记录交互API出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create-issue', methods=['POST'])
def api_create_issue():
    """创建问题API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    try:
        data = request.get_json()
        
        required_fields = ['customer_phone', 'title', 'description', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必要字段: {field}'}), 400
        
        # 获取或创建客户
        customer = db_manager.add_customer(phone_number=data['customer_phone'])
        
        # 创建问题
        issue = db_manager.create_issue(
            customer_id=customer.id,
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data.get('priority', 'medium'),
            location=data.get('location')
        )
        
        return jsonify({
            'success': True,
            'issue_id': issue.id,
            'issue_title': issue.title
        })
        
    except Exception as e:
        logger.error(f"创建问题API出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """仪表板统计API"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    try:
        # 今日统计
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        stats = {
            'total_interactions': db_manager.session.query(Interaction).filter(
                Interaction.timestamp.between(start_date, end_date)
            ).count(),
            'new_issues': db_manager.session.query(Issue).filter(
                Issue.created_at.between(start_date, end_date),
                Issue.status == IssueStatus.NEW
            ).count(),
            'pending_issues': db_manager.session.query(Issue).filter(
                Issue.status.in_([IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.PENDING])
            ).count(),
            'resolved_today': db_manager.session.query(Issue).filter(
                Issue.status == IssueStatus.RESOLVED,
                Issue.updated_at.between(start_date, end_date)
            ).count(),
        }
        
        # 最近7天趋势
        trend_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())
            
            day_stats = {
                'date': date.strftime('%Y-%m-%d'),
                'interactions': db_manager.session.query(Interaction).filter(
                    Interaction.timestamp.between(date_start, date_end)
                ).count(),
                'issues': db_manager.session.query(Issue).filter(
                    Issue.created_at.between(date_start, date_end)
                ).count(),
            }
            trend_data.append(day_stats)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'trend_data': trend_data
        })
        
    except Exception as e:
        logger.error(f"获取仪表板统计时出错: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reports')
def reports():
    """报告页面"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html')

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='页面未找到'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"服务器内部错误: {e}")
    return render_template('error.html', error='服务器内部错误'), 500

# 启动应用
if __name__ == '__main__':
    print("=" * 50)
    print("RVM客户服务系统 - Web界面")
    print("=" * 50)
    print(f"访问地址: http://localhost:5000")
    print(f"管理员账号: admin / admin123")
    print(f"客服账号: agent1 / agent123")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)