#!/usr/bin/env python3
"""
RVM客户服务系统 - 简化数据库初始化
使用SQLite和简单ORM
"""

import os
import sqlite3
from datetime import datetime, timedelta
import json

def init_database():
    """初始化SQLite数据库"""
    print("=== RVM客户服务系统数据库初始化 ===")
    
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 数据库路径
    db_path = os.path.join(data_dir, 'rvm_service.db')
    print(f"数据库路径: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建客户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE NOT NULL,
        name TEXT,
        location TEXT,
        rvm_id TEXT,
        last_interaction TIMESTAMP,
        total_interactions INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建交互记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        message TEXT NOT NULL,
        response TEXT,
        issue_type TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        location TEXT,
        rvm_id TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    # 创建问题跟踪表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        issue_type TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    # 创建进度跟踪表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_id INTEGER,
        status_update TEXT NOT NULL,
        notes TEXT,
        updated_by TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (issue_id) REFERENCES issues (id)
    )
    ''')
    
    # 创建关键词配置表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE NOT NULL,
        issue_type TEXT NOT NULL,
        response_template TEXT,
        priority INTEGER DEFAULT 1
    )
    ''')
    
    # 创建回复模板表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT UNIQUE NOT NULL,
        template_text TEXT NOT NULL,
        language TEXT DEFAULT 'zh',
        category TEXT
    )
    ''')
    
    conn.commit()
    print("✅ 数据库表创建完成")
    
    # 插入示例数据
    insert_sample_data(cursor, conn)
    
    # 关闭连接
    conn.close()
    
    print(f"\n✅ 数据库初始化完成")
    print(f"数据库文件: {db_path}")
    print(f"大小: {os.path.getsize(db_path) / 1024:.1f} KB")

def insert_sample_data(cursor, conn):
    """插入示例数据"""
    print("\n=== 插入示例数据 ===")
    
    # 插入示例客户
    customers = [
        ('+60123456789', 'John Tan', 'Dataran Banting', 'RVM-BANTING-001', 
         datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 3, 'active'),
        ('+60129876543', 'Sarah Lee', 'Puchong', 'RVM-PUCHONG-002',
         (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 5, 'active'),
        ('+60135557777', 'David Wong', 'Subang Jaya', 'RVM-SUBANG-003',
         (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'), 2, 'active'),
        ('+60136668888', 'Michelle Chan', 'Shah Alam', 'RVM-SHAHALAM-004',
         (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 1, 'inactive')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO customers 
    (phone_number, name, location, rvm_id, last_interaction, total_interactions, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', customers)
    
    print(f"✅ Inserted {len(customers)} sample customers")
    
    # 获取客户ID
    cursor.execute("SELECT id, phone_number FROM customers")
    customer_map = {phone: cid for cid, phone in cursor.fetchall()}
    
    # 插入示例交互记录
    interactions = []
    issue_types = ["RVM Full", "Machine Fault", "Inquiry", "Complaint", "Praise"]
    
    for phone, customer_id in customer_map.items():
        for i in range(3):  # 每个客户3个交互记录
            issue_type = issue_types[i % len(issue_types)]
            timestamp = (datetime.now() - timedelta(days=i*2)).strftime('%Y-%m-%d %H:%M:%S')
            
            interactions.append((
                customer_id,
                f"{issue_type} - Need attention",
                "Thank you for your feedback. We will handle it promptly.",
                issue_type,
                timestamp,
                'resolved',
                'Dataran Banting' if i % 2 == 0 else 'Puchong',
                f"RVM-{['BANTING','PUCHONG','SUBANG','SHAHALAM'][i % 4]}-00{i+1}"
            ))
    
    cursor.executemany('''
    INSERT INTO interactions 
    (customer_id, message, response, issue_type, timestamp, status, location, rvm_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', interactions)
    
    print(f"✅ Inserted {len(interactions)} sample interactions")
    
    # 插入关键词配置
    keywords = [
        ('full', 'RVM Full', 'Thank you for notifying that the RVM at {RVM location} is full. Our team will clean it within 2 hours.', 1),
        ('fault', 'Machine Fault', 'Sorry for the inconvenience. A technician will arrive at {RVM location} within 1 hour to inspect.', 1),
        ('broken', 'Machine Fault', 'Sorry for the inconvenience. A technician will arrive at {RVM location} within 1 hour to inspect.', 1),
        ('not working', 'Machine Fault', 'Sorry for the inconvenience. A technician will arrive at {RVM location} within 1 hour to inspect.', 1),
        ('inquiry', 'Inquiry', 'Thank you for your inquiry. Please tell us what you would like to know?', 3),
        ('question', 'Inquiry', 'Thank you for your question. Please tell us what you would like to know?', 3),
        ('complaint', 'Complaint', 'We apologize for your dissatisfaction. Please provide details and we will handle it immediately.', 2),
        ('praise', 'Praise', 'Thank you for your praise! We will continue to provide better service.', 4),
        ('thank', 'Praise', 'You are welcome! Thank you for using our service.', 4),
        ('location', 'Inquiry', 'Our RVM locations: 1. Dataran Banting, 2. Puchong, 3. Subang Jaya', 3),
        ('hours', 'Inquiry', 'RVM operating hours: Daily 8:00-22:00', 3),
        ('time', 'Inquiry', 'RVM operating hours: Daily 8:00-22:00', 3),
        ('recycle', 'Inquiry', 'We accept: Plastic bottles, aluminum cans, used cooking oil. Rewards: Points redeemable for cash or gifts.', 3)
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO keywords (keyword, issue_type, response_template, priority)
    VALUES (?, ?, ?, ?)
    ''', keywords)
    
    print(f"✅ Inserted {len(keywords)} keyword configurations")
    
    # 插入回复模板
    templates = [
        ('RVM Full Response', 'Thank you for notifying that the RVM at {RVM location} is full. Our cleaning team will arrive within 2 hours. We will notify you when cleaning is complete. Thank you!', 'en', 'Auto Reply'),
        ('Machine Fault Response', 'Sorry for the inconvenience. The RVM at {RVM location} has a malfunction. Our technician will arrive within 1 hour to inspect and repair. Thank you for your patience.', 'en', 'Auto Reply'),
        ('Inquiry Response', 'Thank you for your inquiry. Regarding {inquiry content}, our answer is: {answer content}. If you have other questions, please contact us anytime.', 'en', 'Auto Reply'),
        ('Complaint Response', 'We sincerely apologize for your dissatisfaction. Regarding {complaint content}, we will investigate and handle it immediately. Our customer service manager will contact you soon.', 'en', 'Manual Reply'),
        ('Praise Response', 'Thank you for your praise! Your satisfaction is our greatest motivation. We will continue to provide better service. Have a great day!', 'en', 'Auto Reply'),
        ('Progress Inquiry Response', 'Regarding the issue you reported ({issue type}), current status: {current status}. Estimated completion time: {estimated time}.', 'en', 'Auto Reply'),
        ('Location Inquiry Response', 'Our RVM locations: 1. Dataran Banting, 2. Puchong, 3. Subang Jaya, 4. Shah Alam. Operating hours: 8:00-22:00 daily.', 'en', 'Auto Reply'),
        ('Operating Hours Response', 'RVM operating hours: Daily from 8:00 AM to 10:00 PM (including weekends and public holidays).', 'en', 'Auto Reply'),
        ('Recycling Items Response', 'We accept: 1. Plastic bottles (PET), 2. Aluminum cans, 3. Used cooking oil. Rewards: Earn points for each item, redeemable for cash or gifts.', 'en', 'Auto Reply'),
        ('Rewards Program Response', 'Our rewards program: 1 point per plastic bottle, 2 points per aluminum can, 5 points per liter of used oil. Redeem 100 points for RM5 cash or equivalent gifts.', 'en', 'Auto Reply')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO templates (template_name, template_text, language, category)
    VALUES (?, ?, ?, ?)
    ''', templates)
    
    print(f"✅ Inserted {len(templates)} response templates")
    
    conn.commit()
    
    # 打印统计信息
    print("\n=== Database Statistics ===")
    for table in ['customers', 'interactions', 'keywords', 'templates']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

if __name__ == "__main__":
    init_database()