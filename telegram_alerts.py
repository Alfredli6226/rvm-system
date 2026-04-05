#!/usr/bin/env python3
"""
Telegram Alerts for RVM System
Sends alerts to Telegram when RVM conditions change
"""

import os
import sqlite3
import json
import time
from datetime import datetime
import requests

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '320861427')  # Your Telegram ID

# Database paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RVM_DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_management.db')
CUSTOMER_DB_PATH = os.path.join(BASE_DIR, 'data', 'rvm_service.db')

def send_telegram_message(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram bot token not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Telegram alert sent: {message[:50]}...")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram send error: {e}")
        return False

def check_rvm_alerts():
    """Check RVM conditions and send alerts"""
    alerts = []
    
    try:
        conn = sqlite3.connect(RVM_DB_PATH)
        cursor = conn.cursor()
        
        # Check RVM locations for issues
        cursor.execute('''
            SELECT id, name, status, capacity, last_cleaning, next_cleaning
            FROM rvm_locations
            WHERE status IN ('maintenance', 'warning')
        ''')
        
        problematic_rvms = cursor.fetchall()
        
        for rvm in problematic_rvms:
            rvm_id, name, status, capacity, last_cleaning, next_cleaning = rvm
            
            if status == 'maintenance':
                alerts.append(f"🔧 <b>Maintenance Required</b>\n"
                            f"RVM: {name}\n"
                            f"Status: {status}\n"
                            f"Capacity: {capacity}")
            
            elif status == 'warning':
                alerts.append(f"⚠️ <b>Warning</b>\n"
                            f"RVM: {name}\n"
                            f"Status: {status}\n"
                            f"Capacity: {capacity}\n"
                            f"Last Cleaning: {last_cleaning or 'N/A'}")
        
        # Check for upcoming cleaning schedules
        cursor.execute('''
            SELECT name, next_cleaning
            FROM rvm_locations
            WHERE next_cleaning IS NOT NULL 
            AND date(next_cleaning) = date('now', '+1 day')
        ''')
        
        upcoming_cleaning = cursor.fetchall()
        
        for rvm in upcoming_cleaning:
            name, next_cleaning = rvm
            alerts.append(f"🧹 <b>Cleaning Scheduled Tomorrow</b>\n"
                         f"RVM: {name}\n"
                         f"Scheduled: {next_cleaning}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    return alerts

def check_customer_service():
    """Check customer service statistics"""
    stats = []
    
    try:
        conn = sqlite3.connect(CUSTOMER_DB_PATH)
        cursor = conn.cursor()
        
        # Get today's interactions
        cursor.execute('''
            SELECT COUNT(*) 
            FROM interactions 
            WHERE date(created_at) = date('now')
        ''')
        
        today_interactions = cursor.fetchone()[0]
        
        if today_interactions > 10:
            stats.append(f"📞 <b>High Customer Activity</b>\n"
                        f"Today's interactions: {today_interactions}")
        
        # Get unresolved issues
        cursor.execute('''
            SELECT COUNT(*) 
            FROM interactions 
            WHERE status = 'open'
        ''')
        
        open_issues = cursor.fetchone()[0]
        
        if open_issues > 5:
            stats.append(f"🚨 <b>Unresolved Issues</b>\n"
                        f"Open issues: {open_issues}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Customer DB error: {e}")
    
    return stats

def send_daily_summary():
    """Send daily summary report"""
    try:
        conn = sqlite3.connect(RVM_DB_PATH)
        cursor = conn.cursor()
        
        # Get total RVM count
        cursor.execute('SELECT COUNT(*) FROM rvm_locations')
        total_rvms = cursor.fetchone()[0]
        
        # Get active RVM count
        cursor.execute("SELECT COUNT(*) FROM rvm_locations WHERE status = 'active'")
        active_rvms = cursor.fetchone()[0]
        
        # Get maintenance RVM count
        cursor.execute("SELECT COUNT(*) FROM rvm_locations WHERE status = 'maintenance'")
        maintenance_rvms = cursor.fetchone()[0]
        
        conn.close()
        
        # Customer service stats
        customer_conn = sqlite3.connect(CUSTOMER_DB_PATH)
        customer_cursor = customer_conn.cursor()
        
        customer_cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = customer_cursor.fetchone()[0]
        
        customer_cursor.execute("SELECT COUNT(*) FROM interactions WHERE date(created_at) = date('now')")
        today_interactions = customer_cursor.fetchone()[0]
        
        customer_conn.close()
        
        # Create summary message
        summary = f"📊 <b>Daily RVM System Summary</b>\n\n"
        summary += f"🏢 <b>RVM Locations:</b>\n"
        summary += f"• Total: {total_rvms}\n"
        summary += f"• Active: {active_rvms}\n"
        summary += f"• Maintenance: {maintenance_rvms}\n\n"
        
        summary += f"👥 <b>Customer Service:</b>\n"
        summary += f"• Total Customers: {total_customers}\n"
        summary += f"• Today's Interactions: {today_interactions}\n\n"
        
        summary += f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"🌐 <b>Dashboard:</b> http://localhost:5060/rvm-dashboard"
        
        return summary
        
    except Exception as e:
        print(f"❌ Summary error: {e}")
        return None

def main():
    """Main alert monitoring function"""
    print("🚀 Starting RVM Telegram Alert Monitor")
    print(f"📱 Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"💾 RVM Database: {RVM_DB_PATH}")
    print(f"👥 Customer DB: {CUSTOMER_DB_PATH}")
    print("-" * 50)
    
    # Send startup notification
    startup_msg = f"🟢 <b>RVM Alert System Started</b>\n"
    startup_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    startup_msg += f"Monitoring 6 RVM locations\n"
    startup_msg += f"Dashboard: http://localhost:5060/rvm-dashboard"
    
    send_telegram_message(startup_msg)
    
    # Monitoring loop
    alert_count = 0
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking alerts...")
            
            # Check for alerts
            rvm_alerts = check_rvm_alerts()
            customer_stats = check_customer_service()
            
            all_alerts = rvm_alerts + customer_stats
            
            if all_alerts:
                print(f"⚠️ Found {len(all_alerts)} alerts")
                for alert in all_alerts:
                    send_telegram_message(alert)
                    alert_count += 1
                    time.sleep(1)  # Avoid rate limiting
            else:
                print("✅ No alerts found")
            
            # Send daily summary at 9:00 AM
            current_hour = datetime.now().hour
            if current_hour == 9 and datetime.now().minute < 5:
                summary = send_daily_summary()
                if summary:
                    send_telegram_message(summary)
                    print("📊 Daily summary sent")
            
            # Wait before next check (5 minutes)
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping alert monitor...")
            shutdown_msg = f"🔴 <b>RVM Alert System Stopped</b>\n"
            shutdown_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            shutdown_msg += f"Alerts sent: {alert_count}"
            send_telegram_message(shutdown_msg)
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    # Check if Telegram token is configured
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ WARNING: TELEGRAM_BOT_TOKEN environment variable not set")
        print("To configure:")
        print("1. Create bot with @BotFather")
        print("2. Get bot token")
        print("3. Set environment variable:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        print("\nRunning in test mode (alerts will be printed, not sent)")
    
    main()