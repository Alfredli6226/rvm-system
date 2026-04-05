#!/usr/bin/env python3
"""
RVM客户服务系统 - 数据库初始化脚本
初始化SQLite数据库和示例数据
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import db, Customer, Interaction, Issue, Progress
from config.settings import DATABASE_URI

def init_database():
    """初始化数据库"""
    print("=== RVM客户服务系统数据库初始化 ===")
    
    # 确保数据库目录存在
    db_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(db_dir, exist_ok=True)
    
    # 初始化数据库
    db_path = os.path.join(db_dir, 'rvm_customer_service.db')
    print(f"数据库路径: {db_path}")
    
    # 创建所有表
    db.create_all()
    print("✅ 数据库表创建完成")
    
    # 创建示例数据
    create_sample_data()
    
    print("✅ 数据库初始化完成")
    print(f"数据库文件: {db_path}")
    print(f"大小: {os.path.getsize(db_path) / 1024:.1f} KB")

def create_sample_data():
    """创建示例数据"""
    print("\n=== 创建示例数据 ===")
    
    # 清除现有数据
    Customer.query.delete()
    Interaction.query.delete()
    Issue.query.delete()
    Progress.query.delete()
    db.session.commit()
    
    # 创建示例客户
    customers = [
        Customer(
            phone_number="+60123456789",
            name="张三",
            location="Dataran Banting",
            rvm_id="RVM-BANTING-001",
            last_interaction=datetime.now() - timedelta(days=2),
            total_interactions=3,
            status="active"
        ),
        Customer(
            phone_number="+60129876543",
            name="李四",
            location="Puchong",
            rvm_id="RVM-PUCHONG-002",
            last_interaction=datetime.now() - timedelta(days=1),
            total_interactions=5,
            status="active"
        ),
        Customer(
            phone_number="+60135557777",
            name="王五",
            location="Subang Jaya",
            rvm_id="RVM-SUBANG-003",
            last_interaction=datetime.now() - timedelta(hours=12),
            total_interactions=2,
            status="active"
        ),
        Customer(
            phone_number="+60136668888",
            name="陈六",
            location="Shah Alam",
            rvm_id="RVM-SHAHALAM-004",
            last_interaction=datetime.now() - timedelta(days=3),
            total_interactions=1,
            status="inactive"
        )
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    db.session.commit()
    print(f"✅ 创建 {len(customers)} 个示例客户")
    
    # 创建示例交互记录
    interactions = []
    issue_types = ["RVM已满", "机器故障", "咨询", "投诉", "表扬"]
    statuses = ["pending", "in_progress", "resolved", "escalated"]
    
    for i, customer in enumerate(customers):
        for j in range(customer.total_interactions):
            interaction_time = customer.last_interaction - timedelta(days=j*2)
            issue_type = random.choice(issue_types)
            
            interaction = Interaction(
                customer_id=customer.id,
                message=f"{issue_type} - 需要处理",
                response="已收到您的反馈，我们会尽快处理。",
                issue_type=issue_type,
                timestamp=interaction_time,
                status=random.choice(statuses),
                location=customer.location,
                rvm_id=customer.rvm_id
            )
            interactions.append(interaction)
    
    for interaction in interactions:
        db.session.add(interaction)
    
    db.session.commit()
    print(f"✅ 创建 {len(interactions)} 个示例交互记录")
    
    # 创建示例问题跟踪
    issues = []
    for i, customer in enumerate(customers[:2]):  # 前两个客户有问题
        issue = Issue(
            customer_id=customer.id,
            title=f"{customer.location} RVM {issue_types[i]}",
            description=f"{customer.name}报告{customer.location}的RVM{issue_types[i].lower()}",
            issue_type=issue_types[i],
            priority=random.choice(["low", "medium", "high", "urgent"]),
            status=random.choice(["open", "in_progress", "resolved"]),
            assigned_to=f"技术员{i+1}",
            created_at=datetime.now() - timedelta(days=i+1),
            updated_at=datetime.now() - timedelta(hours=i*6)
        )
        issues.append(issue)
    
    for issue in issues:
        db.session.add(issue)
    
    db.session.commit()
    print(f"✅ 创建 {len(issues)} 个示例问题")
    
    # 创建示例进度跟踪
    progresses = []
    for i, issue in enumerate(issues):
        for j in range(3):  # 每个问题3个进度更新
            progress = Progress(
                issue_id=issue.id,
                status_update=f"进度更新 {j+1}: 正在处理{issue.issue_type}",
                notes=f"技术员已到达现场，正在检查设备。阶段{j+1}完成。",
                updated_by=f"技术员{i+1}",
                timestamp=issue.created_at + timedelta(hours=j*4)
            )
            progresses.append(progress)
    
    for progress in progresses:
        db.session.add(progress)
    
    db.session.commit()
    print(f"✅ 创建 {len(progresses)} 个示例进度记录")
    
    # 打印统计信息
    print("\n=== 数据库统计 ===")
    print(f"客户数量: {Customer.query.count()}")
    print(f"交互记录: {Interaction.query.count()}")
    print(f"问题跟踪: {Issue.query.count()}")
    print(f"进度记录: {Progress.query.count()}")

if __name__ == "__main__":
    init_database()