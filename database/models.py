# 数据库模型定义

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, 
    DateTime, Boolean, Float, ForeignKey, Enum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

from config.settings import DATABASE_CONFIG

Base = declarative_base()

# 枚举类型定义
class IssuePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class IssueStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"

class InteractionType(enum.Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    SYSTEM = "system"

class NotificationType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SYSTEM = "system"

# 数据表定义
class Customer(Base):
    """客户信息表"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100))
    email = Column(String(100))
    location = Column(String(200))
    preferred_language = Column(String(10), default='zh')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    interactions = relationship("Interaction", back_populates="customer")
    issues = relationship("Issue", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, phone={self.phone_number}, name={self.name})>"

class Interaction(Base):
    """客户交互记录表"""
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    message = Column(Text, nullable=False)
    reply = Column(Text)
    category = Column(String(50))
    confidence_score = Column(Float)
    location = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_seconds = Column(Integer)  # 响应时间（秒）
    
    # 关系
    customer = relationship("Customer", back_populates="interactions")
    
    def __repr__(self):
        return f"<Interaction(id={self.id}, customer={self.customer_id}, type={self.interaction_type})>"

class Issue(Base):
    """问题跟踪表"""
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM)
    status = Column(Enum(IssueStatus), default=IssueStatus.NEW)
    location = Column(String(200))
    assigned_to = Column(String(100))
    estimated_resolution_time = Column(DateTime)
    actual_resolution_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SLA相关
    sla_response_time = Column(Integer)  # 响应SLA（分钟）
    sla_resolution_time = Column(Integer)  # 解决SLA（小时）
    response_deadline = Column(DateTime)
    resolution_deadline = Column(DateTime)
    
    # 关系
    customer = relationship("Customer", back_populates="issues")
    updates = relationship("IssueUpdate", back_populates="issue")
    
    def __repr__(self):
        return f"<Issue(id={self.id}, title={self.title}, status={self.status})>"

class IssueUpdate(Base):
    """问题更新记录表"""
    __tablename__ = 'issue_updates'
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False)
    update_type = Column(String(50))  # status_change, comment, attachment
    content = Column(Text, nullable=False)
    updated_by = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    issue = relationship("Issue", back_populates="updates")
    
    def __repr__(self):
        return f"<IssueUpdate(id={self.id}, issue={self.issue_id}, type={self.update_type})>"

class RVM(Base):
    """RVM设备信息表"""
    __tablename__ = 'rvms'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    coordinates = Column(String(100))  # 经纬度
    responsible_party = Column(String(100))
    contact_person = Column(String(100))
    contact_number = Column(String(20))
    installation_date = Column(DateTime)
    last_maintenance_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)
    status = Column(String(50), default='active')
    capacity_kg = Column(Integer)
    current_fill_percentage = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RVM(id={self.id}, location={self.location_id}, name={self.name})>"

class CleaningSchedule(Base):
    """清理计划表"""
    __tablename__ = 'cleaning_schedules'
    
    id = Column(Integer, primary_key=True)
    rvm_id = Column(Integer, ForeignKey('rvms.id'), nullable=False)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    actual_date = Column(DateTime)
    responsible_team = Column(String(100))
    status = Column(String(50), default='scheduled')  # scheduled, in_progress, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    rvm = relationship("RVM")
    
    def __repr__(self):
        return f"<CleaningSchedule(id={self.id}, rvm={self.rvm_id}, date={self.scheduled_date})>"

class Notification(Base):
    """通知记录表"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    notification_type = Column(Enum(NotificationType), nullable=False)
    recipient = Column(String(200), nullable=False)
    subject = Column(String(200))
    content = Column(Text, nullable=False)
    status = Column(String(50), default='pending')  # pending, sent, failed, delivered
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, recipient={self.recipient})>"

class Report(Base):
    """报告记录表"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)  # 报告数据
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_to = Column(String(500))
    
    def __repr__(self):
        return f"<Report(id={self.id}, type={self.report_type}, period={self.period_start})>"

class TemplateUsage(Base):
    """模板使用统计表"""
    __tablename__ = 'template_usage'
    
    id = Column(Integer, primary_key=True)
    template_id = Column(String(100), nullable=False, index=True)
    category = Column(String(50))
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TemplateUsage(id={self.id}, template={self.template_id}, count={self.usage_count})>"

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    log_level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(100))
    function = Column(String(100))
    message = Column(Text, nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level={self.log_level}, message={self.message[:50]})>"

class User(Base):
    """系统用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(50), default='agent')  # admin, manager, agent
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

# 创建数据库引擎和会话
engine = create_engine(
    DATABASE_CONFIG["path"],
    echo=DATABASE_CONFIG["echo"],
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据访问辅助函数
class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def close(self):
        self.session.close()
    
    def add_customer(self, phone_number, name=None, email=None, location=None):
        """添加或更新客户"""
        customer = self.session.query(Customer).filter_by(phone_number=phone_number).first()
        if customer:
            # 更新现有客户
            if name:
                customer.name = name
            if email:
                customer.email = email
            if location:
                customer.location = location
            customer.updated_at = datetime.utcnow()
        else:
            # 创建新客户
            customer = Customer(
                phone_number=phone_number,
                name=name,
                email=email,
                location=location
            )
            self.session.add(customer)
        
        self.session.commit()
        return customer
    
    def log_interaction(self, customer_id, interaction_type, message, reply=None, 
                       category=None, confidence_score=None, location=None):
        """记录客户交互"""
        interaction = Interaction(
            customer_id=customer_id,
            interaction_type=interaction_type,
            message=message,
            reply=reply,
            category=category,
            confidence_score=confidence_score,
            location=location
        )
        self.session.add(interaction)
        self.session.commit()
        return interaction
    
    def create_issue(self, customer_id, title, description, category, 
                    priority=IssuePriority.MEDIUM, location=None):
        """创建问题记录"""
        issue = Issue(
            customer_id=customer_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            location=location,
            status=IssueStatus.NEW,
            created_at=datetime.utcnow()
        )
        self.session.add(issue)
        self.session.commit()
        return issue
    
    def update_issue_status(self, issue_id, new_status, update_content=None, updated_by=None):
        """更新问题状态"""
        issue = self.session.query(Issue).get(issue_id)
        if not issue:
            return None
        
        old_status = issue.status
        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        
        # 记录状态更新
        if update_content:
            update = IssueUpdate(
                issue_id=issue_id,
                update_type='status_change',
                content=f"状态从 {old_status.value} 变更为 {new_status.value}\n{update_content}",
                updated_by=updated_by
            )
            self.session.add(update)
        
        self.session.commit()
        return issue
    
    def get_pending_issues(self, limit=50):
        """获取待处理问题"""
        return self.session.query(Issue).filter(
            Issue.status.in_([IssueStatus.NEW, IssueStatus.IN_PROGRESS, IssueStatus.PENDING])
        ).order_by(Issue.created_at.desc()).limit(limit).all()
    
    def get_customer_interactions(self, customer_id, limit=20):
        """获取客户交互历史"""
        return self.session.query(Interaction).filter_by(
            customer_id=customer_id
        ).order_by(Interaction.timestamp.desc()).limit(limit).all()
    
    def get_daily_stats(self, date=None):
        """获取每日统计"""
        if not date:
            date = datetime.utcnow().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        stats = {
            'total_interactions': self.session.query(Interaction).filter(
                Interaction.timestamp.between(start_date, end_date)
            ).count(),
            'new_issues': self.session.query(Issue).filter(
                Issue.created_at.between(start_date, end_date)
            ).count(),
            'resolved_issues': self.session.query(Issue).filter(
                Issue.status == IssueStatus.RESOLVED,
                Issue.updated_at.between(start_date, end_date)
            ).count(),
        }
        
        return stats

# 导出
__all__ = [
    'Base',
    'Customer',
    'Interaction',
    'InteractionType',
    'Issue',
    'IssuePriority',
    'IssueStatus',
    'IssueUpdate',
    'RVM',
    'CleaningSchedule',
    'Notification',
    'NotificationType',
    'Report',
    'TemplateUsage',
    'SystemLog',
    'User',
    'engine',
    'SessionLocal',
    'init_db',
    'get_db',
    'DatabaseManager',
]