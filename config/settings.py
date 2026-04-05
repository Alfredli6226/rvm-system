# RVM客户服务系统配置

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "database" / "customer_service.db"

# 确保目录存在
for directory in [DATA_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# 数据库配置
DATABASE_CONFIG = {
    "path": str(DB_PATH),
    "echo": False,  # SQL日志
    "pool_size": 10,
    "max_overflow": 20,
}

# WhatsApp配置
WHATSAPP_CONFIG = {
    "business_number": "+601110728228",
    "customer_service_hours": {
        "weekdays": "8:00-18:00",
        "weekends": "9:00-17:00",
    },
    "auto_reply_enabled": True,
    "response_time_target": 15,  # 分钟
}

# RVM位置配置
RVM_LOCATIONS = {
    "dataran_banting": {
        "name": "Dataran Banting",
        "address": "Dataran Banting, Selangor",
        "responsible_party": "KDEBS",
        "contact": "+603-XXXX XXXX",
        "cleaning_frequency": "每周2次",
    },
    "subang_jaya": {
        "name": "Subang Jaya",
        "address": "Subang Jaya, Selangor",
        "responsible_party": "KDEBS",
        "contact": "+603-XXXX XXXX",
        "cleaning_frequency": "每周3次",
    },
    "puchong": {
        "name": "Puchong",
        "address": "Puchong, Selangor",
        "responsible_party": "KDEBS",
        "contact": "+603-XXXX XXXX",
        "cleaning_frequency": "每周2次",
    },
}

# 服务级别协议
SLA_CONFIG = {
    "response_time": {
        "urgent": 15,  # 分钟
        "normal": 30,  # 分钟
        "low": 60,     # 分钟
    },
    "resolution_time": {
        "rvm_full": 48,  # 小时
        "technical_issue": 24,  # 小时
        "general_inquiry": 4,   # 小时
    },
    "escalation_levels": {
        "level1": "客服代表",
        "level2": "主管",
        "level3": "经理",
        "level4": "总监",
    },
}

# 自动回复配置
AUTO_REPLY_CONFIG = {
    "enabled": True,
    "confidence_threshold": 0.7,  # 置信度阈值
    "fallback_to_human": True,    # 低置信度转人工
    "max_auto_replies": 3,        # 最大自动回复次数
    "cooldown_minutes": 5,        # 冷却时间
}

# 通知配置
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "from_email": "noreply@hmadigital.asia",
        "admin_emails": ["admin@hmadigital.asia", "alfredli@hmadigital.asia"],
    },
    "telegram": {
        "enabled": True,
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
    },
    "whatsapp": {
        "enabled": False,  # 需要WhatsApp Business API
        "webhook_url": os.getenv("WHATSAPP_WEBHOOK_URL", ""),
    },
}

# 报告配置
REPORT_CONFIG = {
    "daily_report": {
        "enabled": True,
        "time": "08:00",  # 每天8点生成
        "recipients": ["admin@hmadigital.asia"],
    },
    "weekly_report": {
        "enabled": True,
        "day": "monday",  # 每周一
        "time": "09:00",
        "recipients": ["admin@hmadigital.asia", "management@hmadigital.asia"],
    },
    "monthly_report": {
        "enabled": True,
        "day": 1,  # 每月1号
        "time": "10:00",
        "recipients": ["admin@hmadigital.asia", "management@hmadigital.asia", "investors@hmadigital.asia"],
    },
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "customer_service.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "DEBUG",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "sqlalchemy": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# 安全配置
SECURITY_CONFIG = {
    "api_key": os.getenv("API_KEY", "default-secret-key-change-in-production"),
    "session_timeout": 3600,  # 1小时
    "max_login_attempts": 5,
    "lockout_minutes": 15,
    "password_min_length": 8,
    "require_2fa": False,
}

# 备份配置
BACKUP_CONFIG = {
    "enabled": True,
    "frequency": "daily",  # daily, weekly, monthly
    "time": "02:00",  # 备份时间
    "retention_days": 30,
    "cloud_storage": {
        "enabled": False,
        "provider": "aws_s3",  # aws_s3, google_cloud, azure
        "bucket": os.getenv("BACKUP_BUCKET", ""),
    },
}

# 性能配置
PERFORMANCE_CONFIG = {
    "cache_ttl": 300,  # 5分钟
    "max_concurrent_requests": 100,
    "rate_limit": {
        "per_minute": 60,
        "per_hour": 1000,
    },
    "database_timeout": 30,  # 秒
}

# 主题配置
THEME_CONFIG = {
    "primary_color": "#2E7D32",  # 绿色
    "secondary_color": "#FFC107",  # 黄色
    "accent_color": "#2196F3",  # 蓝色
    "dark_mode": True,
    "language": "zh",  # zh, en, ms
}

# 测试配置
TEST_CONFIG = {
    "test_database": ":memory:",
    "test_mode": False,
    "mock_external_apis": True,
}

# 版本信息
VERSION = "1.0.0"
LAST_UPDATED = "2026-04-05"

# 导出所有配置
__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "LOG_DIR",
    "DB_PATH",
    "DATABASE_CONFIG",
    "WHATSAPP_CONFIG",
    "RVM_LOCATIONS",
    "SLA_CONFIG",
    "AUTO_REPLY_CONFIG",
    "NOTIFICATION_CONFIG",
    "REPORT_CONFIG",
    "LOGGING_CONFIG",
    "SECURITY_CONFIG",
    "BACKUP_CONFIG",
    "PERFORMANCE_CONFIG",
    "THEME_CONFIG",
    "TEST_CONFIG",
    "VERSION",
    "LAST_UPDATED",
]