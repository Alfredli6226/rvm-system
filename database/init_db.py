#!/usr/bin/env python3
# 数据库初始化脚本

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, DatabaseManager, RVM, CleaningSchedule, User
from config.settings import RVM_LOCATIONS
import hashlib

def create_sample_data():
    """创建示例数据"""
    db = DatabaseManager()
    
    try:
        print("📊 创建示例数据...")
        
        # 创建RVM设备
        print("  创建RVM设备...")
        for location_id, location_info in RVM_LOCATIONS.items():
            rvm = RVM(
                location_id=location_id,
                name=location_info['name'],
                address=location_info['address'],
                responsible_party=location_info['responsible_party'],
                contact_number=location_info['contact'],
                status='active',
                capacity_kg=500,
                current_fill_percentage=30,
                installation_date=datetime.utcnow() - timedelta(days=90)
            )
            db.session.add(rvm)
        
        db.session.commit()
        print("  ✅ RVM设备创建完成")
        
        # 创建清理计划
        print("  创建清理计划...")
        rvms = db.session.query(RVM).all()
        for rvm in rvms:
            # 明天的清理计划
            tomorrow = datetime.utcnow() + timedelta(days=1)
            schedule = CleaningSchedule(
                rvm_id=rvm.id,
                scheduled_date=tomorrow.replace(hour=10, minute=0, second=0),
                responsible_team="KDEBS清理团队",
                status='scheduled'
            )
            db.session.add(schedule)
            
            # 后天的清理计划
            day_after = tomorrow + timedelta(days=1)
            schedule2 = CleaningSchedule(
                rvm_id=rvm.id,
                scheduled_date=day_after.replace(hour=14, minute=0, second=0),
                responsible_team="KDEBS清理团队",
                status='scheduled'
            )
            db.session.add(schedule2)
        
        db.session.commit()
        print("  ✅ 清理计划创建完成")
        
        # 创建示例用户
        print("  创建示例用户...")
        # 管理员用户
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        admin = User(
            username="admin",
            email="admin@hmadigital.asia",
            password_hash=admin_password,
            full_name="系统管理员",
            role="admin"
        )
        db.session.add(admin)
        
        # 客服用户
        agent_password = hashlib.sha256("agent123".encode()).hexdigest()
        agent = User(
            username="agent1",
            email="agent1@hmadigital.asia",
            password_hash=agent_password,
            full_name="客服代表1",
            role="agent"
        )
        db.session.add(agent)
        
        db.session.commit()
        print("  ✅ 示例用户创建完成")
        
        print("\n🎉 示例数据创建完成！")
        print("\n📋 创建的数据：")
        print(f"  • RVM设备: {len(rvms)} 个")
        print(f"  • 清理计划: {len(rvms) * 2} 个")
        print(f"  • 系统用户: 2 个")
        
    except Exception as e:
        print(f"❌ 创建示例数据时出错: {e}")
        db.session.rollback()
        raise
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 50)
    print("RVM客户服务系统 - 数据库初始化")
    print("=" * 50)
    
    try:
        # 初始化数据库表
        print("\n1️⃣ 创建数据库表...")
        init_db()
        print("   ✅ 数据库表创建完成")
        
        # 创建示例数据
        print("\n2️⃣ 是否创建示例数据？")
        print("   (输入 'y' 创建示例数据，其他键跳过)")
        choice = input("   选择: ").strip().lower()
        
        if choice == 'y':
            create_sample_data()
        else:
            print("   ⏭️ 跳过示例数据创建")
        
        print("\n" + "=" * 50)
        print("🎉 数据库初始化完成！")
        print("=" * 50)
        print("\n📁 数据库文件位置:")
        print(f"   {os.path.abspath('customer_service.db')}")
        print("\n🚀 下一步:")
        print("   1. 启动Web界面: python web/app.py")
        print("   2. 访问系统: http://localhost:5000")
        print("   3. 使用以下账号登录:")
        print("      • 管理员: admin / admin123")
        print("      • 客服: agent1 / agent123")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()