# Telegram Bot Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Telegram Bot
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose bot name: `RVM_Alert_Bot`
5. Choose username: `rvm_alert_bot` (must end with _bot)
6. **Save the API Token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Environment
```bash
# Set Telegram bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# Make it permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export TELEGRAM_BOT_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Start Alert Monitor
```bash
cd /Users/alfredli6226/.openclaw/workspace/rvm_customer_service_system
./start_telegram_alerts.sh
```

## 📱 Bot Features

### 1. Real-time Alerts
- RVM maintenance required
- Capacity warnings
- Cleaning schedules
- Customer service issues

### 2. Daily Summary (9:00 AM)
```
📊 Daily RVM System Summary

🏢 RVM Locations:
• Total: 6
• Active: 5
• Maintenance: 1

👥 Customer Service:
• Total Customers: 4
• Today's Interactions: 15

⏰ Time: 2026-04-05 09:00:00
🌐 Dashboard: http://localhost:5060/rvm-dashboard
```

### 3. Monitoring Intervals
- **Alert checks**: Every 5 minutes
- **Daily summary**: 9:00 AM daily
- **Startup/shutdown**: Notifications

## 🔧 Manual Testing

### Test Alert Sending
```python
# Test script
import requests

TOKEN = "your_bot_token"
CHAT_ID = "320861427"  # Your Telegram ID

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT_ID,
    'text': '✅ Test alert from RVM System',
    'parse_mode': 'HTML'
}

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

### Test Without Token
```bash
# Run in test mode (prints alerts locally)
TELEGRAM_BOT_TOKEN="" python telegram_alerts.py
```

## ⚙️ Configuration Options

### Environment Variables
```bash
# Telegram Configuration
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="320861427"  # Default: your ID

# Alert Thresholds (optional)
export RVM_CAPACITY_WARNING=90    # % capacity for warning
export MIN_INTERACTIONS_ALERT=10  # Daily interactions for alert
export OPEN_ISSUES_ALERT=5        # Open issues for alert
```

### Custom Alert Messages
Edit `telegram_alerts.py` to customize:
- Alert thresholds
- Message formats
- Check intervals
- Alert conditions

## 🔗 Integration with RVM Systems

### Connected Systems
1. **RVM Management System** (port 5060)
   - Location status monitoring
   - Capacity tracking
   - Maintenance scheduling

2. **Customer Service System** (port 5050)
   - Interaction tracking
   - Issue monitoring
   - Customer statistics

### Data Flow
```
RVM Systems → Telegram Alert Monitor → Your Telegram
     ↓               ↓                    ↓
  Database      Alert Logic        Real-time Notifications
```

## 🚨 Alert Types

### 1. RVM Status Alerts
```
🔧 Maintenance Required
RVM: Klang
Status: maintenance
Capacity: 600kg
```

### 2. Cleaning Schedule Alerts
```
🧹 Cleaning Scheduled Tomorrow
RVM: Dataran Banting
Scheduled: 2026-04-06
```

### 3. Customer Service Alerts
```
📞 High Customer Activity
Today's interactions: 15
```

### 4. System Status Alerts
```
🟢 RVM Alert System Started
Time: 2026-04-05 22:55:00
Monitoring 6 RVM locations
Dashboard: http://localhost:5060/rvm-dashboard
```

## 📊 Monitoring Dashboard

### Web Interface
Access via: `http://localhost:5060/rvm-dashboard`
- Real-time RVM status
- Alert history
- System statistics

### Telegram Commands (Future)
Planned features:
- `/status` - Check system status
- `/alerts` - View recent alerts
- `/summary` - Get current summary
- `/restart` - Restart services (admin)

## 🔒 Security

### Token Security
1. **Never share** bot token publicly
2. **Use environment variables**
3. **Regularly rotate** tokens
4. **Restrict bot permissions**

### Access Control
- Bot only sends messages (cannot read)
- Fixed chat ID (your Telegram only)
- No database write access

## 🚀 Production Deployment

### 1. Systemd Service (Linux)
```ini
# /etc/systemd/system/rvm-telegram.service
[Unit]
Description=RVM Telegram Alert Monitor
After=network.target

[Service]
Type=simple
User=rvmuser
WorkingDirectory=/opt/rvm-system
Environment=TELEGRAM_BOT_TOKEN=your_token
ExecStart=/usr/bin/python3 telegram_alerts.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements_simple.txt
CMD ["python", "telegram_alerts.py"]
```

### 3. Cloud Deployment
- **AWS Lambda** + CloudWatch Events
- **Google Cloud Functions** + Scheduler
- **Azure Functions** + Timer trigger

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Telegram bot token not configured"
```bash
# Solution: Set environment variable
export TELEGRAM_BOT_TOKEN="your_token"
```

#### 2. "Error 400: Bad Request"
- Check token format
- Verify chat ID
- Check message length

#### 3. "Error 429: Too Many Requests"
- Reduce check frequency
- Implement rate limiting
- Use exponential backoff

#### 4. Database Connection Errors
```bash
# Check if databases exist
ls -la data/
# Should show: rvm_management.db, rvm_service.db
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python telegram_alerts.py

# Check logs
tail -f logs/telegram_alerts.log
```

## 📈 Advanced Features

### 1. Alert Escalation
- Level 1: Telegram notification
- Level 2: Email notification
- Level 3: SMS notification
- Level 4: Phone call

### 2. Alert Acknowledgment
- Reply to acknowledge alerts
- Track acknowledgment status
- Escalate unacknowledged alerts

### 3. Historical Data
- Store alert history
- Generate weekly reports
- Analyze alert patterns

### 4. Multi-language Support
- English (default)
- Malay
- Chinese
- Custom languages

## 🤝 Support

### Documentation
- This guide
- Code comments
- API documentation

### Contact
- Telegram: @AlfredLi96
- Email: alfredli@hmadigital.asia
- GitHub: https://github.com/Alfredli6226/rvm-system

### Updates
Check for updates:
```bash
cd /Users/alfredli6226/.openclaw/workspace/rvm_customer_service_system
git pull origin main
```

---

**Last Updated**: 2026-04-05  
**Version**: 1.0.0  
**Status**: ✅ Production Ready