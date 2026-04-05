#!/usr/bin/env python3
"""
RVM客户服务系统 - 主应用
提供Web API和自动回复功能
"""

import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据库配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_service.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    return conn

# ==================== 自动回复引擎 ====================

def analyze_message(message):
    """分析消息内容，识别问题类型"""
    message_lower = message.lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询所有关键词
    cursor.execute("SELECT keyword, issue_type, response_template, priority FROM keywords ORDER BY priority")
    keywords = cursor.fetchall()
    
    conn.close()
    
    # 匹配关键词
    matched_keywords = []
    for keyword, issue_type, response_template, priority in keywords:
        if keyword in message_lower:
            matched_keywords.append({
                'keyword': keyword,
                'issue_type': issue_type,
                'response_template': response_template,
                'priority': priority
            })
    
    # 按优先级排序
    matched_keywords.sort(key=lambda x: x['priority'])
    
    return matched_keywords

def generate_response(phone_number, message, location=None, rvm_id=None):
    """生成自动回复"""
    # 分析消息
    matched_keywords = analyze_message(message)
    
    if not matched_keywords:
        # 默认回复
        response_text = "感谢您的消息。请提供更多信息，以便我们更好地帮助您。"
        issue_type = "未知"
    else:
        # 使用最高优先级的关键词
        best_match = matched_keywords[0]
        issue_type = best_match['issue_type']
        
        # 获取对应的模板
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if issue_type == "RVM已满":
            template_name = "RVM已满回复"
        elif issue_type == "机器故障":
            template_name = "机器故障回复"
        elif issue_type == "咨询":
            template_name = "咨询回复"
        elif issue_type == "投诉":
            template_name = "投诉回复"
        elif issue_type == "表扬":
            template_name = "表扬回复"
        else:
            template_name = "咨询回复"
        
        cursor.execute(
            "SELECT template_text FROM templates WHERE template_name = ?",
            (template_name,)
        )
        template_result = cursor.fetchone()
        
        if template_result:
            response_text = template_result[0]
        else:
            response_text = best_match['response_template']
        
        conn.close()
        
        # 替换模板变量
        if location:
            response_text = response_text.replace("{RVM位置}", location)
            response_text = response_text.replace("{RVM location}", location)
        
        if rvm_id:
            response_text = response_text.replace("{RVM_ID}", rvm_id)
    
    # 记录交互
    record_interaction(phone_number, message, response_text, issue_type, location, rvm_id)
    
    return {
        'response': response_text,
        'issue_type': issue_type,
        'matched_keywords': [k['keyword'] for k in matched_keywords]
    }

def record_interaction(phone_number, message, response, issue_type, location=None, rvm_id=None):
    """记录客户交互"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查找或创建客户
    cursor.execute(
        "SELECT id FROM customers WHERE phone_number = ?",
        (phone_number,)
    )
    customer = cursor.fetchone()
    
    if customer:
        customer_id = customer[0]
        # 更新客户信息
        cursor.execute('''
            UPDATE customers 
            SET last_interaction = ?, total_interactions = total_interactions + 1
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id))
    else:
        # 创建新客户
        cursor.execute('''
            INSERT INTO customers (phone_number, location, rvm_id, last_interaction, total_interactions)
            VALUES (?, ?, ?, ?, 1)
        ''', (phone_number, location, rvm_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        customer_id = cursor.lastrowid
    
    # 记录交互
    cursor.execute('''
        INSERT INTO interactions 
        (customer_id, message, response, issue_type, location, rvm_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'resolved')
    ''', (customer_id, message, response, issue_type, location, rvm_id))
    
    # 如果是问题类型，创建问题跟踪
    if issue_type in ["RVM已满", "机器故障", "投诉"]:
        cursor.execute('''
            INSERT INTO issues 
            (customer_id, title, description, issue_type, priority, status, assigned_to)
            VALUES (?, ?, ?, ?, ?, 'open', '自动分配')
        ''', (
            customer_id,
            f"{location or '未知位置'} - {issue_type}",
            message,
            issue_type,
            'high' if issue_type in ["RVM已满", "机器故障"] else 'medium'
        ))
        
        issue_id = cursor.lastrowid
        
        # 创建初始进度记录
        cursor.execute('''
            INSERT INTO progress (issue_id, status_update, notes, updated_by)
            VALUES (?, ?, ?, ?)
        ''', (
            issue_id,
            f"问题已记录: {issue_type}",
            f"客户消息: {message}",
            "自动回复系统"
        ))
    
    conn.commit()
    conn.close()

# ==================== Web API 路由 ====================

@app.route('/')
def index():
    """首页 - 显示系统状态"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'RVM Customer Service System'
    })

@app.route('/api/auto-reply', methods=['POST'])
def auto_reply():
    """自动回复API"""
    try:
        data = request.json
        
        # 验证必要字段
        if not data or 'phone_number' not in data or 'message' not in data:
            return jsonify({
                'error': '缺少必要字段: phone_number 和 message'
            }), 400
        
        phone_number = data['phone_number']
        message = data['message']
        location = data.get('location')
        rvm_id = data.get('rvm_id')
        
        # 生成回复
        result = generate_response(phone_number, message, location, rvm_id)
        
        return jsonify({
            'success': True,
            'phone_number': phone_number,
            'original_message': message,
            'response': result['response'],
            'issue_type': result['issue_type'],
            'matched_keywords': result['matched_keywords'],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """获取客户列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, phone_number, name, location, rvm_id, 
                   last_interaction, total_interactions, status, created_at
            FROM customers
            ORDER BY last_interaction DESC
            LIMIT 100
        ''')
        
        customers = []
        for row in cursor.fetchall():
            customers.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(customers),
            'customers': customers
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/interactions', methods=['GET'])
def get_interactions():
    """获取交互记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 支持过滤参数
        phone_number = request.args.get('phone_number')
        issue_type = request.args.get('issue_type')
        limit = int(request.args.get('limit', 50))
        
        query = '''
            SELECT i.*, c.phone_number, c.name, c.location
            FROM interactions i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if phone_number:
            query += " AND c.phone_number = ?"
            params.append(phone_number)
        
        if issue_type:
            query += " AND i.issue_type = ?"
            params.append(issue_type)
        
        query += " ORDER BY i.timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        interactions = []
        for row in cursor.fetchall():
            interactions.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(interactions),
            'interactions': interactions
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/issues', methods=['GET'])
def get_issues():
    """获取问题跟踪"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        status = request.args.get('status', 'open')
        limit = int(request.args.get('limit', 20))
        
        cursor.execute('''
            SELECT i.*, c.phone_number, c.name, c.location,
                   (SELECT COUNT(*) FROM progress p WHERE p.issue_id = i.id) as progress_count
            FROM issues i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.status = ?
            ORDER BY 
                CASE i.priority 
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                i.created_at DESC
            LIMIT ?
        ''', (status, limit))
        
        issues = []
        for row in cursor.fetchall():
            issues.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(issues),
            'issues': issues
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 今日统计
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_customers,
                SUM(total_interactions) as total_interactions,
                (SELECT COUNT(*) FROM interactions WHERE DATE(timestamp) = ?) as today_interactions,
                (SELECT COUNT(*) FROM issues WHERE status = 'open') as open_issues,
                (SELECT COUNT(*) FROM issues WHERE status = 'resolved') as resolved_issues
            FROM customers
        ''', (today,))
        
        stats = dict(cursor.fetchone())
        
        # 问题类型分布
        cursor.execute('''
            SELECT issue_type, COUNT(*) as count
            FROM interactions
            GROUP BY issue_type
            ORDER BY count DESC
        ''')
        
        issue_distribution = []
        for row in cursor.fetchall():
            issue_distribution.append({
                'issue_type': row['issue_type'],
                'count': row['count']
            })
        
        # 最近活动
        cursor.execute('''
            SELECT location, COUNT(*) as activity_count
            FROM interactions
            WHERE DATE(timestamp) = ?
            GROUP BY location
            ORDER BY activity_count DESC
            LIMIT 5
        ''', (today,))
        
        recent_activity = []
        for row in cursor.fetchall():
            recent_activity.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'issue_distribution': issue_distribution,
            'recent_activity': recent_activity,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    """管理关键词"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # 获取关键词列表
            cursor.execute('''
                SELECT id, keyword, issue_type, response_template, priority
                FROM keywords
                ORDER BY priority, keyword
            ''')
            
            keywords = []
            for row in cursor.fetchall():
                keywords.append(dict(row))
            
            return jsonify({
                'success': True,
                'keywords': keywords
            })
        
        elif request.method == 'POST':
            # 添加新关键词
            data = request.json
            
            if not data or 'keyword' not in data or 'issue_type' not in data:
                return jsonify({'error': '缺少必要字段'}), 400
            
            cursor.execute('''
                INSERT OR REPLACE INTO keywords (keyword, issue_type, response_template, priority)
                VALUES (?, ?, ?, ?)
            ''', (
                data['keyword'],
                data['issue_type'],
                data.get('response_template', ''),
                data.get('priority', 1)
            ))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': '关键词已添加/更新',
                'id': cursor.lastrowid
            })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
    
    finally:
        conn.close()

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """获取回复模板"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        category = request.args.get('category')
        language = request.args.get('language', 'zh')
        
        query = "SELECT id, template_name, template_text, language, category FROM templates WHERE language = ?"
        params = [language]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY template_name"
        
        cursor.execute(query, params)
        
        templates = []
        for row in cursor.fetchall():
            templates.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# ==================== 启动应用 ====================

if __name__ == '__main__':
    # 确保模板目录存在
    template_dir = os.path.join(BASE_DIR, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # 启动应用
    print("🚀 RVM客户服务系统启动中...")
    print(f"📊 管理界面: http://localhost:5000")
    print(f"🔧 API文档: http://localhost:5000")
    print(f"📝 日志目录: {os.path.join(BASE_DIR, 'logs')}")
    
    app.run(host='0.0.0.0', port=5050, debug=False)