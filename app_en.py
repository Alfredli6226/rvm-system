#!/usr/bin/env python3
"""
RVM Customer Service System - Main Application
Provides Web API and auto-reply functionality in English
"""

import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_service.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return dictionary format
    return conn

# ==================== Auto-Reply Engine ====================

def analyze_message(message):
    """Analyze message content, identify issue type"""
    message_lower = message.lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query all keywords
    cursor.execute("SELECT keyword, issue_type, response_template, priority FROM keywords ORDER BY priority")
    keywords = cursor.fetchall()
    
    conn.close()
    
    # Match keywords
    matched_keywords = []
    for keyword, issue_type, response_template, priority in keywords:
        if keyword in message_lower:
            matched_keywords.append({
                'keyword': keyword,
                'issue_type': issue_type,
                'response_template': response_template,
                'priority': priority
            })
    
    # Sort by priority
    matched_keywords.sort(key=lambda x: x['priority'])
    
    return matched_keywords

def generate_response(phone_number, message, location=None, rvm_id=None):
    """Generate auto-reply"""
    # Analyze message
    matched_keywords = analyze_message(message)
    
    if not matched_keywords:
        # Default response
        response_text = "Thank you for your message. Please provide more information so we can assist you better."
        issue_type = "Unknown"
    else:
        # Use highest priority keyword
        best_match = matched_keywords[0]
        issue_type = best_match['issue_type']
        
        # Get corresponding template
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if issue_type == "RVM Full":
            template_name = "RVM Full Response"
        elif issue_type == "Machine Fault":
            template_name = "Machine Fault Response"
        elif issue_type == "Inquiry":
            template_name = "Inquiry Response"
        elif issue_type == "Complaint":
            template_name = "Complaint Response"
        elif issue_type == "Praise":
            template_name = "Praise Response"
        else:
            template_name = "Inquiry Response"
        
        cursor.execute(
            "SELECT template_text FROM templates WHERE template_name = ? AND language = 'en'",
            (template_name,)
        )
        template_result = cursor.fetchone()
        
        if template_result:
            response_text = template_result[0]
        else:
            response_text = best_match['response_template']
        
        conn.close()
        
        # Replace template variables
        if location:
            response_text = response_text.replace("{RVM location}", location)
            response_text = response_text.replace("{RVM位置}", location)  # Fallback
        
        if rvm_id:
            response_text = response_text.replace("{RVM_ID}", rvm_id)
    
    # Record interaction
    record_interaction(phone_number, message, response_text, issue_type, location, rvm_id)
    
    return {
        'response': response_text,
        'issue_type': issue_type,
        'matched_keywords': [k['keyword'] for k in matched_keywords]
    }

def record_interaction(phone_number, message, response, issue_type, location=None, rvm_id=None):
    """Record customer interaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find or create customer
    cursor.execute(
        "SELECT id FROM customers WHERE phone_number = ?",
        (phone_number,)
    )
    customer = cursor.fetchone()
    
    if customer:
        customer_id = customer[0]
        # Update customer info
        cursor.execute('''
            UPDATE customers 
            SET last_interaction = ?, total_interactions = total_interactions + 1
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), customer_id))
    else:
        # Create new customer
        cursor.execute('''
            INSERT INTO customers (phone_number, location, rvm_id, last_interaction, total_interactions)
            VALUES (?, ?, ?, ?, 1)
        ''', (phone_number, location, rvm_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        customer_id = cursor.lastrowid
    
    # Record interaction
    cursor.execute('''
        INSERT INTO interactions 
        (customer_id, message, response, issue_type, location, rvm_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'resolved')
    ''', (customer_id, message, response, issue_type, location, rvm_id))
    
    # If it's an issue type, create issue tracking
    if issue_type in ["RVM Full", "Machine Fault", "Complaint"]:
        cursor.execute('''
            INSERT INTO issues 
            (customer_id, title, description, issue_type, priority, status, assigned_to)
            VALUES (?, ?, ?, ?, ?, 'open', 'Auto-assigned')
        ''', (
            customer_id,
            f"{location or 'Unknown location'} - {issue_type}",
            message,
            issue_type,
            'high' if issue_type in ["RVM Full", "Machine Fault"] else 'medium'
        ))
        
        issue_id = cursor.lastrowid
        
        # Create initial progress record
        cursor.execute('''
            INSERT INTO progress (issue_id, status_update, notes, updated_by)
            VALUES (?, ?, ?, ?)
        ''', (
            issue_id,
            f"Issue recorded: {issue_type}",
            f"Customer message: {message}",
            "Auto-reply System"
        ))
    
    conn.commit()
    conn.close()

# ==================== Web API Routes ====================

@app.route('/')
def index():
    """Home page - Show system status"""
    return render_template('index_en.html')

@app.route('/api/health')
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'RVM Customer Service System',
        'version': '1.0.0',
        'language': 'English'
    })

@app.route('/api/auto-reply', methods=['POST'])
def auto_reply():
    """Auto-reply API"""
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'phone_number' not in data or 'message' not in data:
            return jsonify({
                'error': 'Missing required fields: phone_number and message'
            }), 400
        
        phone_number = data['phone_number']
        message = data['message']
        location = data.get('location')
        rvm_id = data.get('rvm_id')
        
        # Generate response
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
            'timestamp': datetime.now().isoformat(),
            'message': 'Internal server error'
        }), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get customer list"""
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
            'error': str(e),
            'message': 'Failed to retrieve customers'
        }), 500

@app.route('/api/interactions', methods=['GET'])
def get_interactions():
    """Get interaction records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Support filter parameters
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
            'error': str(e),
            'message': 'Failed to retrieve interactions'
        }), 500

@app.route('/api/issues', methods=['GET'])
def get_issues():
    """Get issue tracking"""
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
            'error': str(e),
            'message': 'Failed to retrieve issues'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Today's statistics
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
        
        # Issue type distribution
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
        
        # Recent activity
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
            'error': str(e),
            'message': 'Failed to retrieve statistics'
        }), 500

@app.route('/api/keywords', methods=['GET', 'POST'])
def manage_keywords():
    """Manage keywords"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # Get keyword list
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
            # Add new keyword
            data = request.json
            
            if not data or 'keyword' not in data or 'issue_type' not in data:
                return jsonify({'error': 'Missing required fields'}), 400
            
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
                'message': 'Keyword added/updated successfully',
                'id': cursor.lastrowid
            })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to manage keywords'
        }), 500
    
    finally:
        conn.close()

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get response templates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        category = request.args.get('category')
        language = request.args.get('language', 'en')
        
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
            'error': str(e),
            'message': 'Failed to retrieve templates'
        }), 500

# ==================== Start Application ====================

if __name__ == '__main__':
    # Ensure template directory exists
    template_dir = os.path.join(BASE_DIR, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Start application
    print("🚀 RVM Customer Service System starting...")
    print(f"📊 Admin Interface: http://localhost:5050")
    print(f"🔧 API Documentation: http://localhost:5050")
    print(f"📝 Log Directory: {os.path.join(BASE_DIR, 'logs')}")
    print(f"🌐 Language: English")
    
    app.run(host='0.0.0.0', port=5050, debug=False)