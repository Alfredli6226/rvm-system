# RVM Customer Service & Management System

## 🚀 System Overview

A complete RVM (Reverse Vending Machine) management solution with:
1. **Customer Service System** - English auto-reply engine
2. **RVM Management Dashboard** - Complete location management
3. **Real-time Monitoring** - Live statistics and alerts
4. **Integrated API** - Seamless data flow between systems

## 🌐 Live Systems

### 1. Customer Service System (English Version)
- **URL**: http://localhost:5050
- **Port**: 5050
- **Features**: Auto-reply, customer management, interaction tracking

### 2. RVM Management Dashboard
- **URL**: http://localhost:5060/rvm-dashboard
- **Port**: 5060
- **Features**: 6 RVM locations, statistics, charts, alerts, quick actions

## 📁 System Structure

```
rvm_customer_service_system/
├── README.md                    # System documentation
├── requirements_simple.txt      # Python dependencies (simplified)
├── app_en.py                    # Customer Service System (English)
├── rvm_management.py           # RVM Management Dashboard
├── templates/
│   ├── index_en.html           # Customer Service Admin (English)
│   └── rvm_dashboard.html      # RVM Management Dashboard
├── data/
│   ├── rvm_service.db          # Customer Service Database
│   ├── rvm_management.db       # RVM Management Database
│   └── rvm_locations.json      # RVM Locations Data (6 locations)
├── scripts/
│   ├── run_en.sh               # Start Customer Service System
│   ├── run_rvm_management.sh   # Start RVM Management System
│   ├── stop_en.sh              # Stop Customer Service
│   ├── status_en.sh            # Check Service Status
│   └── fix_db.py               # Database repair utilities
├── init_database.py            # Customer Service DB init
├── init_rvm_database.py        # RVM Management DB init
└── .gitignore                  # Git exclusion rules
```

## 🔧 Quick Start

### 1. Start Customer Service System (English)
```bash
cd rvm_customer_service_system
./run_en.sh
# Access: http://localhost:5050
```

### 2. Start RVM Management System
```bash
./run_rvm_management.sh
# Access: http://localhost:5060/rvm-dashboard
```

### 3. Test APIs
```bash
# Customer Service Health
curl http://localhost:5050/api/health

# RVM Management Health
curl http://localhost:5060/api/rvm/health

# All RVM Locations
curl http://localhost:5060/api/rvm/locations
```

### 4. Test Auto-Reply
```bash
# Test RVM full scenario
curl -X POST http://localhost:5050/api/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "RVM is full", "phone_number": "+60123456789"}'

# Test machine fault
curl -X POST http://localhost:5050/api/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Machine not working", "phone_number": "+60123456789"}'
```

## 📊 核心功能

### 1. 自动回复系统
- **关键词匹配**：识别客户问题类型
- **智能回复**：根据问题自动选择模板
- **上下文记忆**：记住之前的对话
- **人工接管**：复杂问题转人工

### 2. 客户服务数据库
- **客户信息**：姓名、联系方式、位置
- **服务记录**：所有交互历史
- **问题分类**：RVM已满、故障、咨询等
- **解决状态**：待处理、处理中、已解决

### 3. 进度跟踪系统
- **清理进度**：KDEBS清理状态
- **时间线**：从通知到完成的完整时间线
- **提醒系统**：超时自动提醒
- **实时更新**：进度变化实时通知

### 4. 报告生成系统
- **每日报告**：当天服务统计
- **每周报告**：服务趋势分析
- **客户满意度**：反馈统计
- **问题热点**：常见问题分析

## 🎯 关键词匹配规则

### RVM已满相关关键词
- "RVM已满"、"满了"、"装满了"
- "清理"、"清空"、"收集"
- "Dataran Banting"、"Subang Jaya"、"Puchong"

### 进度查询关键词
- "进度"、"怎么样了"、"什么时候"
- "完成了吗"、"好了吗"、"可以了吗"

### 故障报告关键词
- "坏了"、"故障"、"不能用"
- "卡住了"、"没反应"、"错误"

### 一般咨询关键词
- "怎么用"、"如何使用"、"操作"
- "时间"、"营业时间"、"开放时间"
- "价格"、"费用"、"收费"

## 💬 回复模板系统

### 模板结构
```json
{
  "category": "rvm_full",
  "keywords": ["RVM已满", "满了", "装满了"],
  "templates": [
    {
      "name": "standard_reply",
      "content": "感谢您通知我们{location}RVM已满的情况！...",
      "variables": ["location"]
    }
  ]
}
```

### 变量替换
- `{location}` - RVM位置
- `{customer_name}` - 客户姓名
- `{estimated_time}` - 预计时间
- `{contact_number}` - 联系方式

## 📱 WhatsApp集成

### 手动模式
1. 复制模板回复
2. 在WhatsApp中发送
3. 在系统中记录交互

### 半自动模式
1. 系统生成回复
2. 人工确认发送
3. 自动记录到数据库

### 全自动模式（需要API）
1. WhatsApp Business API
2. 自动接收消息
3. 自动回复
4. 自动记录

## 🔌 API接口

### 获取回复
```
GET /api/get_reply?message=Dataran+Banting+RVM已满
```

### 记录交互
```
POST /api/log_interaction
{
  "customer_phone": "+6011XXXXXXX",
  "message": "RVM已满",
  "reply": "感谢通知...",
  "status": "pending"
}
```

### 获取进度
```
GET /api/get_progress?location=Dataran+Banting
```

## 📈 报告系统

### 每日报告内容
- 总交互次数
- 问题分类统计
- 平均响应时间
- 解决率
- 客户满意度

### 每周报告内容
- 趋势分析
- 热点问题
- 服务改进建议
- 团队表现

## 🔒 安全与隐私

### 数据保护
- 客户信息加密存储
- 访问权限控制
- 数据备份策略
- GDPR合规

### 系统安全
- 输入验证
- SQL注入防护
- 会话管理
- 日志审计

## 🚀 部署选项

### 本地部署
- 适合小型团队
- 数据完全控制
- 低成本

### 云部署
- 高可用性
- 自动扩展
- 专业维护

### 混合部署
- 本地数据库
- 云处理服务
- 灵活配置

## 📞 支持与维护

### 技术支持
- 系统文档
- 故障排除指南
- 更新日志

### 培训材料
- 用户手册
- 视频教程
- 最佳实践

### 联系方式
- 技术支持：tech@hmadigital.asia
- 紧急联系：+60 11-1095 8228

## 🔄 更新计划

### 短期目标（1个月）
- [ ] 基础自动回复
- [ ] 客户数据库
- [ ] Web界面
- [ ] 基本报告

### 中期目标（3个月）
- [ ] WhatsApp API集成
- [ ] 高级分析
- [ ] 移动应用
- [ ] 多语言支持

### 长期目标（6个月）
- [ ] AI智能回复
- [ ] 预测分析
- [ ] 集成CRM
- [ ] 自动化工作流

---

## 💡 使用建议

### 开始阶段
1. 使用手动模式熟悉系统
2. 收集常见问题优化关键词
3. 培训团队使用标准流程

### 扩展阶段
1. 逐步增加自动化功能
2. 集成现有系统
3. 优化客户体验

### 成熟阶段
1. 全面自动化
2. 数据驱动决策
3. 持续优化改进

---

**版本：1.0 | 更新：2026-04-05**