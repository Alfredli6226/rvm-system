#!/usr/bin/env python3
"""
RVM Management System - Complete Dashboard
Management dashboard for all RVM locations
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_management.db')
CUSTOMER_DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_service.db')

def get_db_connection(db_path=DB_PATH):
    """Get database connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== RVM Management API ====================

@app.route('/rvm-dashboard')
def rvm_dashboard():
    """RVM Management Dashboard"""
    return render_template('rvm_dashboard.html')

@app.route('/api/rvm/health')
def rvm_health_check():
    """RVM Management Health Check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'RVM Management System',
        'version': '2.0.0'
    })

@app.route('/api/rvm/locations', methods=['GET'])
def get_rvm_locations():
    """Get all RVM locations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, address, status, capacity, installed_date, 
                   last_cleaning, next_cleaning, contact_person, contact_phone,
                   coordinates, operating_hours, accepted_items, rewards_rate,
                   notes, created_at, updated_at
            FROM rvm_locations
            ORDER BY 
                CASE status 
                    WHEN 'active' THEN 1
                    WHEN 'maintenance' THEN 2
                    WHEN 'inactive' THEN 3
                    ELSE 4
                END,
                name
        ''')
        
        locations = []
        for row in cursor.fetchall():
            location = dict(row)
            # Parse JSON fields
            if location['coordinates']:
                location['coordinates'] = json.loads(location['coordinates'])
            if location['accepted_items']:
                location['accepted_items'] = json.loads(location['accepted_items'])
            locations.append(location)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(locations),
            'locations': locations
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve RVM locations'
        }), 500

@app.route('/api/rvm/locations/<rvm_id>', methods=['GET'])
def get_rvm_location(rvm_id):
    """Get specific RVM location details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM rvm_locations WHERE id = ?
        ''', (rvm_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'error': f'RVM location {rvm_id} not found'
            }), 404
        
        location = dict(row)
        
        # Parse JSON fields
        if location['coordinates']:
            location['coordinates'] = json.loads(location['coordinates'])
        if location['accepted_items']:
            location['accepted_items'] = json.loads(location['accepted_items'])
        
        # Get recent collections
        cursor.execute('''
            SELECT * FROM rvm_collections 
            WHERE rvm_id = ? 
            ORDER BY collection_date DESC 
            LIMIT 10
        ''', (rvm_id,))
        
        collections = [dict(row) for row in cursor.fetchall()]
        
        # Get recent maintenance
        cursor.execute('''
            SELECT * FROM rvm_maintenance 
            WHERE rvm_id = ? 
            ORDER BY maintenance_date DESC 
            LIMIT 5
        ''', (rvm_id,))
        
        maintenance = [dict(row) for row in cursor.fetchall()]
        
        # Get recent metrics
        cursor.execute('''
            SELECT * FROM rvm_metrics 
            WHERE rvm_id = ? 
            ORDER BY metric_date DESC 
            LIMIT 30
        ''', (rvm_id,))
        
        metrics = [dict(row) for row in cursor.fetchall()]
        
        # Get active alerts
        cursor.execute('''
            SELECT * FROM rvm_alerts 
            WHERE rvm_id = ? AND status = 'active'
            ORDER BY alert_date DESC
        ''', (rvm_id,))
        
        alerts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'location': location,
            'recent_collections': collections,
            'recent_maintenance': maintenance,
            'recent_metrics': metrics,
            'active_alerts': alerts
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f'Failed to retrieve RVM location {rvm_id}'
        }), 500

@app.route('/api/rvm/collections', methods=['GET'])
def get_rvm_collections():
    """Get RVM collection records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Filter parameters
        rvm_id = request.args.get('rvm_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        query = '''
            SELECT c.*, l.name as rvm_name, l.address
            FROM rvm_collections c
            LEFT JOIN rvm_locations l ON c.rvm_id = l.id
            WHERE 1=1
        '''
        params = []
        
        if rvm_id:
            query += " AND c.rvm_id = ?"
            params.append(rvm_id)
        
        if start_date:
            query += " AND c.collection_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND c.collection_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY c.collection_date DESC, c.collection_time DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        collections = []
        for row in cursor.fetchall():
            collections.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(collections),
            'collections': collections
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve collection records'
        }), 500

@app.route('/api/rvm/maintenance', methods=['GET'])
def get_rvm_maintenance():
    """Get RVM maintenance records"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        rvm_id = request.args.get('rvm_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 20))
        
        query = '''
            SELECT m.*, l.name as rvm_name, l.address
            FROM rvm_maintenance m
            LEFT JOIN rvm_locations l ON m.rvm_id = l.id
            WHERE 1=1
        '''
        params = []
        
        if rvm_id:
            query += " AND m.rvm_id = ?"
            params.append(rvm_id)
        
        if status:
            query += " AND m.status = ?"
            params.append(status)
        
        query += " ORDER BY m.maintenance_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        maintenance = []
        for row in cursor.fetchall():
            maintenance.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(maintenance),
            'maintenance': maintenance
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve maintenance records'
        }), 500

@app.route('/api/rvm/metrics', methods=['GET'])
def get_rvm_metrics():
    """Get RVM performance metrics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        rvm_id = request.args.get('rvm_id')
        period = request.args.get('period', '7d')  # 7d, 30d, 90d
        
        # Calculate date range
        end_date = datetime.now()
        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=7)
        
        query = '''
            SELECT m.*, l.name as rvm_name
            FROM rvm_metrics m
            LEFT JOIN rvm_locations l ON m.rvm_id = l.id
            WHERE m.metric_date BETWEEN ? AND ?
        '''
        params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if rvm_id:
            query += " AND m.rvm_id = ?"
            params.append(rvm_id)
        
        query += " ORDER BY m.metric_date"
        
        cursor.execute(query, params)
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(metrics),
            'period': period,
            'metrics': metrics
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve performance metrics'
        }), 500

@app.route('/api/rvm/alerts', methods=['GET'])
def get_rvm_alerts():
    """Get RVM alerts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        status = request.args.get('status', 'active')
        alert_level = request.args.get('alert_level')
        limit = int(request.args.get('limit', 20))
        
        query = '''
            SELECT a.*, l.name as rvm_name, l.address, l.status as rvm_status
            FROM rvm_alerts a
            LEFT JOIN rvm_locations l ON a.rvm_id = l.id
            WHERE a.status = ?
        '''
        params = [status]
        
        if alert_level:
            query += " AND a.alert_level = ?"
            params.append(alert_level)
        
        query += " ORDER BY a.alert_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': alerts
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve alerts'
        }), 500

@app.route('/api/rvm/overview', methods=['GET'])
def get_rvm_overview():
    """Get RVM system overview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get location statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_rvms,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_rvms,
                SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance_rvms,
                SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_rvms
            FROM rvm_locations
        ''')
        location_stats = dict(cursor.fetchone())
        
        # Get collection statistics (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT 
                COUNT(*) as total_collections,
                SUM(total_weight_kg) as total_weight,
                SUM(rewards_points) as total_points,
                AVG(total_weight_kg) as avg_daily_weight
            FROM rvm_collections
            WHERE collection_date >= ?
        ''', (seven_days_ago,))
        collection_stats = dict(cursor.fetchone())
        
        # Get maintenance statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_maintenance,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_maintenance,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_maintenance,
                SUM(cost) as total_maintenance_cost
            FROM rvm_maintenance
            WHERE maintenance_date >= ?
        ''', (seven_days_ago,))
        maintenance_stats = dict(cursor.fetchone())
        
        # Get alert statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_alerts,
                SUM(CASE WHEN alert_level = 'critical' THEN 1 ELSE 0 END) as critical_alerts,
                SUM(CASE WHEN alert_level = 'warning' THEN 1 ELSE 0 END) as warning_alerts,
                SUM(CASE WHEN alert_level = 'info' THEN 1 ELSE 0 END) as info_alerts
            FROM rvm_alerts
            WHERE alert_date >= ?
        ''', (seven_days_ago,))
        alert_stats = dict(cursor.fetchone())
        
        # Get top performing RVMs (by collection weight)
        cursor.execute('''
            SELECT 
                l.id, l.name, 
                SUM(c.total_weight_kg) as total_collection,
                COUNT(c.id) as collection_count,
                AVG(c.total_weight_kg) as avg_collection
            FROM rvm_locations l
            LEFT JOIN rvm_collections c ON l.id = c.rvm_id
            WHERE c.collection_date >= ?
            GROUP BY l.id, l.name
            ORDER BY total_collection DESC
            LIMIT 5
        ''', (seven_days_ago,))
        
        top_rvms = []
        for row in cursor.fetchall():
            top_rvms.append(dict(row))
        
        # Get recent collections timeline
        cursor.execute('''
            SELECT 
                collection_date,
                COUNT(*) as collection_count,
                SUM(total_weight_kg) as total_weight
            FROM rvm_collections
            WHERE collection_date >= ?
            GROUP BY collection_date
            ORDER BY collection_date DESC
            LIMIT 7
        ''', (seven_days_ago,))
        
        timeline = []
        for row in cursor.fetchall():
            timeline.append(dict(row))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'overview': {
                'location_stats': location_stats,
                'collection_stats': collection_stats,
                'maintenance_stats': maintenance_stats,
                'alert_stats': alert_stats
            },
            'top_performing_rvms': top_rvms,
            'recent_timeline': timeline,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve system overview'
        }), 500

@app.route('/api/rvm/integrated-stats', methods=['GET'])
def get_integrated_stats():
    """Get integrated statistics from both databases"""
    try:
        # Get RVM management stats
        conn1 = get_db_connection(DB_PATH)
        cursor1 = conn1.cursor()
        
        cursor1.execute('SELECT COUNT(*) as total_rvms FROM rvm_locations')
        rvm_count = cursor1.fetchone()[0]
        
        cursor1.execute('''
            SELECT SUM(total_weight_kg) as weekly_collection 
            FROM rvm_collections 
            WHERE collection_date >= date('now', '-7 days')
        ''')
        weekly_collection = cursor1.fetchone()[0] or 0
        
        conn1.close()
        
        # Get customer service stats
        conn2 = get_db_connection(CUSTOMER_DB_PATH)
        cursor2 = conn2.cursor()
        
        cursor2.execute('SELECT COUNT(*) as total_customers FROM customers')
        customer_count = cursor2.fetchone()[0]
        
        cursor2.execute('''
            SELECT COUNT(*) as today_interactions 
            FROM interactions 
            WHERE DATE(timestamp) = DATE('now')
        ''')
        today_interactions = cursor2.fetchone()[0]
        
        cursor2.execute('''
            SELECT issue_type, COUNT(*) as count
            FROM interactions
            WHERE DATE(timestamp) >= date('now', '-7 days')
            GROUP BY issue_type
            ORDER BY count DESC
        ''')
        
        issue_distribution = []
        for row in cursor2.fetchall():
            issue_distribution.append({
                'issue_type': row['issue_type'],
                'count': row['count']
            })
        
        conn2.close()
        
        return jsonify({
            'success': True,
            'integrated_stats': {
                'rvm_count': rvm_count,
                'weekly_collection_kg': weekly_collection,
                'customer_count': customer_count,
                'today_interactions': today_interactions,
                'issue_distribution': issue_distribution
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to retrieve integrated statistics'
        }), 500

# ==================== Start Application ====================

if __name__ == '__main__':
    # Ensure template directory exists
    template_dir = os.path.join(BASE_DIR, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Initialize RVM management database if not exists
    if not os.path.exists(DB_PATH):
        print("Initializing RVM management database...")
        import init_rvm_database
        init_rvm_database.init_rvm_database()
    
    # Start application
    print("🚀 RVM Management System starting...")
    print(f"📊 Management Dashboard: http://localhost:5060")
    print(f"🔧 API Documentation: http://localhost:5060/rvm-dashboard")
    print(f"📝 Log Directory: {os.path.join(BASE_DIR, 'logs')}")
    print(f"🌐 Integrated System: RVM Management + Customer Service")
    
    app.run(host='0.0.0.0', port=5060, debug=False)