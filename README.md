# RVM Customer Service & Management System

## 🚀 Live Systems

### 1. Customer Service System (English)
- **URL**: http://localhost:5050
- **Port**: 5050
- **Status**: ✅ Running (PID: 62601)
- **Features**: Auto-reply engine, customer management, interaction tracking

### 2. RVM Management Dashboard
- **URL**: http://localhost:5060/rvm-dashboard
- **Port**: 5060
- **Status**: ✅ Running (PID: 62977)
- **Features**: 6 RVM locations, real-time statistics, charts, alerts, quick actions

## 📊 RVM Locations Managed

| Location | Status | Capacity | Contact |
|----------|--------|----------|---------|
| Dataran Banting | 🟢 Active | 500kg | John Tan (+60123456789) |
| Puchong | 🟢 Active | 750kg | Sarah Lee (+60129876543) |
| Subang Jaya | 🟢 Active | 1000kg | Mike Wong (+60135556677) |
| Shah Alam | 🟢 Active | 800kg | Lisa Chen (+60137778899) |
| Klang | 🟡 Maintenance | 600kg | David Lim (+60134445566) |
| Petaling Jaya | 🟢 Active | 900kg | Emma Tan (+60136667788) |

## 🔧 Quick Start Commands

```bash
# Start Customer Service System
cd /Users/alfredli6226/.openclaw/workspace/rvm_customer_service_system
./run_en.sh

# Start RVM Management System
./run_rvm_management.sh

# Check status
./status_en.sh
ps aux | grep -E "(rvm_management|app_en)"
```

## 📡 API Endpoints

### Customer Service System (Port 5050)
```
GET  /api/health                    # Health check
POST /api/process-message          # Process customer message
GET  /api/customers                # List all customers
GET  /api/stats                    # System statistics
```

### RVM Management System (Port 5060)
```
GET  /api/rvm/health               # Health check
GET  /api/rvm/locations            # All RVM locations
GET  /api/rvm/overview             # System overview
GET  /api/rvm/alerts               # Active alerts
GET  /rvm-dashboard                # Dashboard UI
```

## 🎯 Test Scenarios

### 1. RVM Full Notification
```bash
curl -X POST http://localhost:5050/api/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "RVM is full at Dataran Banting", "phone_number": "+60123456789"}'
```

### 2. Machine Fault Report
```bash
curl -X POST http://localhost:5050/api/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Machine not working in Puchong", "phone_number": "+60129876543"}'
```

### 3. General Inquiry
```bash
curl -X POST http://localhost:5050/api/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the operating hours?", "phone_number": "+60135556677"}'
```

## 📁 Project Structure

```
rvm_customer_service_system/
├── app_en.py                    # Customer Service System (English)
├── rvm_management.py           # RVM Management Dashboard
├── templates/
│   ├── index_en.html           # Customer Service Admin
│   └── rvm_dashboard.html      # RVM Dashboard
├── data/
│   ├── rvm_service.db          # Customer Service Database
│   ├── rvm_management.db       # RVM Management Database
│   └── rvm_locations.json      # 6 RVM locations data
├── scripts/
│   ├── run_en.sh               # Start Customer Service
│   ├── run_rvm_management.sh   # Start RVM Management
│   ├── stop_en.sh              # Stop services
│   └── status_en.sh            # Check status
└── requirements_simple.txt     # Dependencies
```

## 🚀 Deployment Options

### Local Development
```bash
# Both systems running locally
./run_en.sh & ./run_rvm_management.sh
```

### Production Deployment
1. **Docker containers** for each service
2. **Nginx reverse proxy** for port 80/443
3. **Database backups** automated
4. **Monitoring** with alerts

### Cloud Deployment
- **AWS/Azure/Google Cloud**
- **Heroku/Render** (PaaS)
- **Your VPS** with proper security

## 🔗 Integration with Existing Backend

This system is ready to integrate with your existing backend:

1. **Database connection** - Direct SQL access
2. **API integration** - RESTful API endpoints
3. **Real-time data sync** - Bidirectional data flow
4. **Unified dashboard** - Single interface for all systems

## 📞 Support

- **System Status**: Check `./status_en.sh`
- **Logs**: `logs/` directory
- **Database**: `data/` directory
- **Issues**: GitHub repository issues

---

**Version**: 2.0.0  
**Last Updated**: 2026-04-05  
**Status**: ✅ Production Ready  
**Next Steps**: Integration with existing backend systems