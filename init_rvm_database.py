#!/usr/bin/env python3
"""
RVM Management System - Database Initialization
Extended database with RVM locations and management
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta

def init_rvm_database():
    """Initialize RVM management database"""
    print("=== RVM Management System Database Initialization ===")
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Database path
    db_path = os.path.join(data_dir, 'rvm_management.db')
    print(f"Database path: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create RVM locations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rvm_locations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT,
        status TEXT DEFAULT 'active',
        capacity TEXT,
        installed_date TEXT,
        last_cleaning TEXT,
        next_cleaning TEXT,
        contact_person TEXT,
        contact_phone TEXT,
        coordinates TEXT,  -- JSON string: {"lat": 0.0, "lng": 0.0}
        operating_hours TEXT,
        accepted_items TEXT,  -- JSON string array
        rewards_rate TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create RVM collection records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rvm_collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rvm_id TEXT,
        collection_date TEXT NOT NULL,
        collection_time TEXT,
        collected_by TEXT,
        plastic_bottles_kg REAL DEFAULT 0,
        aluminum_cans_kg REAL DEFAULT 0,
        used_oil_liters REAL DEFAULT 0,
        paper_kg REAL DEFAULT 0,
        glass_kg REAL DEFAULT 0,
        electronics_kg REAL DEFAULT 0,
        total_weight_kg REAL DEFAULT 0,
        rewards_points INTEGER DEFAULT 0,
        notes TEXT,
        status TEXT DEFAULT 'completed',
        FOREIGN KEY (rvm_id) REFERENCES rvm_locations (id)
    )
    ''')
    
    # Create RVM maintenance records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rvm_maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rvm_id TEXT,
        maintenance_date TEXT NOT NULL,
        maintenance_type TEXT,
        technician TEXT,
        description TEXT,
        parts_replaced TEXT,
        cost REAL DEFAULT 0,
        duration_hours REAL DEFAULT 1,
        status TEXT DEFAULT 'completed',
        notes TEXT,
        next_maintenance TEXT,
        FOREIGN KEY (rvm_id) REFERENCES rvm_locations (id)
    )
    ''')
    
    # Create RVM performance metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rvm_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rvm_id TEXT,
        metric_date TEXT NOT NULL,
        daily_collection_kg REAL DEFAULT 0,
        daily_customers INTEGER DEFAULT 0,
        daily_rewards_points INTEGER DEFAULT 0,
        uptime_percentage REAL DEFAULT 100,
        avg_collection_time_minutes REAL DEFAULT 0,
        customer_satisfaction_score REAL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (rvm_id) REFERENCES rvm_locations (id)
    )
    ''')
    
    # Create RVM alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rvm_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rvm_id TEXT,
        alert_type TEXT NOT NULL,
        alert_level TEXT DEFAULT 'warning',
        alert_message TEXT NOT NULL,
        alert_date TEXT NOT NULL,
        resolved_date TEXT,
        resolved_by TEXT,
        resolution_notes TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (rvm_id) REFERENCES rvm_locations (id)
    )
    ''')
    
    conn.commit()
    print("✅ Database tables created")
    
    # Load RVM locations from JSON
    load_rvm_locations(cursor, conn)
    
    # Insert sample collection records
    insert_sample_collections(cursor, conn)
    
    # Insert sample maintenance records
    insert_sample_maintenance(cursor, conn)
    
    # Insert sample metrics
    insert_sample_metrics(cursor, conn)
    
    # Insert sample alerts
    insert_sample_alerts(cursor, conn)
    
    conn.close()
    
    print(f"\n✅ RVM Management database initialization complete")
    print(f"Database file: {db_path}")
    print(f"Size: {os.path.getsize(db_path) / 1024:.1f} KB")

def load_rvm_locations(cursor, conn):
    """Load RVM locations from JSON file"""
    print("\n=== Loading RVM locations ===")
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'rvm_locations.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        rvm_locations = data['rvm_locations']
        
        for location in rvm_locations:
            # Convert lists/dicts to JSON strings
            coordinates_json = json.dumps(location.get('coordinates', {}))
            accepted_items_json = json.dumps(location.get('accepted_items', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO rvm_locations 
                (id, name, address, status, capacity, installed_date, last_cleaning, 
                 next_cleaning, contact_person, contact_phone, coordinates, 
                 operating_hours, accepted_items, rewards_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location['id'],
                location['name'],
                location['address'],
                location['status'],
                location['capacity'],
                location['installed_date'],
                location['last_cleaning'],
                location['next_cleaning'],
                location['contact_person'],
                location['contact_phone'],
                coordinates_json,
                location['operating_hours'],
                accepted_items_json,
                location['rewards_rate']
            ))
        
        print(f"✅ Loaded {len(rvm_locations)} RVM locations")
        
    except Exception as e:
        print(f"❌ Error loading RVM locations: {e}")
        # Create default locations if JSON file doesn't exist
        create_default_locations(cursor, conn)

def create_default_locations(cursor, conn):
    """Create default RVM locations"""
    default_locations = [
        ('RVM-BANTING-001', 'Dataran Banting', 'Dataran Banting, Selangor', 'active', '500kg', 
         '2026-03-11', '2026-04-05', '2026-04-06', 'John Tan', '+60123456789',
         '{"lat": 2.8133, "lng": 101.4974}', '8:00-22:00', 
         '["plastic_bottles", "aluminum_cans", "used_oil"]', '1 point per item'),
        
        ('RVM-PUCHONG-002', 'Puchong', 'Puchong, Selangor', 'active', '750kg',
         '2026-02-15', '2026-04-04', '2026-04-07', 'Sarah Lee', '+60129876543',
         '{"lat": 3.0449, "lng": 101.6206}', '8:00-22:00',
         '["plastic_bottles", "aluminum_cans", "used_oil", "paper"]', '1.2 points per item'),
        
        ('RVM-SUBANG-003', 'Subang Jaya', 'Subang Jaya, Selangor', 'active', '1000kg',
         '2026-01-20', '2026-04-03', '2026-04-08', 'David Wong', '+60135557777',
         '{"lat": 3.0497, "lng": 101.5854}', '8:00-22:00',
         '["plastic_bottles", "aluminum_cans", "used_oil", "paper", "glass"]', '1.5 points per item'),
        
        ('RVM-SHAHALAM-004', 'Shah Alam', 'Shah Alam, Selangor', 'active', '800kg',
         '2026-02-28', '2026-04-02', '2026-04-09', 'Michelle Chan', '+60136668888',
         '{"lat": 3.0733, "lng": 101.5185}', '8:00-22:00',
         '["plastic_bottles", "aluminum_cans", "used_oil"]', '1 point per item'),
        
        ('RVM-KLANG-005', 'Klang', 'Klang, Selangor', 'maintenance', '600kg',
         '2026-03-05', '2026-04-01', '2026-04-10', 'Robert Lim', '+60137779999',
         '{"lat": 3.0449, "lng": 101.4455}', '8:00-22:00',
         '["plastic_bottles", "aluminum_cans", "used_oil"]', '1 point per item'),
        
        ('RVM-PETALING-006', 'Petaling Jaya', 'Petaling Jaya, Selangor', 'active', '900kg',
         '2026-03-18', '2026-03-31', '2026-04-11', 'Lisa Ng', '+60138881111',
         '{"lat": 3.1073, "lng": 101.6067}', '8:00-22:00',
         '["plastic_bottles", "aluminum_cans", "used_oil", "paper", "glass", "electronics"]', '2 points per item')
    ]
    
    for location in default_locations:
        cursor.execute('''
            INSERT OR REPLACE INTO rvm_locations 
            (id, name, address, status, capacity, installed_date, last_cleaning, 
             next_cleaning, contact_person, contact_phone, coordinates, 
             operating_hours, accepted_items, rewards_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', location)
    
    print(f"✅ Created {len(default_locations)} default RVM locations")

def insert_sample_collections(cursor, conn):
    """Insert sample collection records"""
    print("\n=== Inserting sample collection records ===")
    
    rvm_ids = ['RVM-BANTING-001', 'RVM-PUCHONG-002', 'RVM-SUBANG-003', 
               'RVM-SHAHALAM-004', 'RVM-PETALING-006']
    
    collections = []
    today = datetime.now()
    
    for i, rvm_id in enumerate(rvm_ids):
        for j in range(7):  # Last 7 days
            collection_date = (today - timedelta(days=j)).strftime('%Y-%m-%d')
            
            # Vary collection amounts
            plastic = 50 + (i * 10) + (j * 5)
            aluminum = 20 + (i * 5) + (j * 3)
            oil = 15 + (i * 3) + (j * 2)
            paper = 10 + (i * 2) if i > 1 else 0
            glass = 8 + i if i > 2 else 0
            electronics = 5 if i == 5 else 0
            
            total_weight = plastic + aluminum + paper + glass + electronics
            rewards_points = int((plastic * 1) + (aluminum * 2) + (oil * 5) + (paper * 0.5) + (glass * 1) + (electronics * 10))
            
            collections.append((
                rvm_id,
                collection_date,
                f"{8 + (j % 12)}:00",
                f"Technician {i+1}",
                plastic,
                aluminum,
                oil,
                paper,
                glass,
                electronics,
                total_weight,
                rewards_points,
                f"Regular collection - Day {j+1}",
                'completed'
            ))
    
    cursor.executemany('''
        INSERT INTO rvm_collections 
        (rvm_id, collection_date, collection_time, collected_by, 
         plastic_bottles_kg, aluminum_cans_kg, used_oil_liters, 
         paper_kg, glass_kg, electronics_kg, total_weight_kg, 
         rewards_points, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', collections)
    
    print(f"✅ Inserted {len(collections)} sample collection records")

def insert_sample_maintenance(cursor, conn):
    """Insert sample maintenance records"""
    print("\n=== Inserting sample maintenance records ===")
    
    maintenance_records = [
        ('RVM-BANTING-001', '2026-04-01', 'Routine Check', 'Tech John', 
         'Routine maintenance and cleaning', 'Filters, Sensors', 150.00, 2, 
         'completed', 'All systems functioning normally', '2026-05-01'),
        
        ('RVM-PUCHONG-002', '2026-03-28', 'Sensor Replacement', 'Tech Sarah', 
         'Replaced faulty weight sensors', 'Weight Sensors x2', 320.50, 3, 
         'completed', 'Sensors calibrated and tested', '2026-04-28'),
        
        ('RVM-SUBANG-003', '2026-03-25', 'Software Update', 'Tech David', 
         'Updated system software to v2.5', 'None', 0, 1, 
         'completed', 'Software update successful', '2026-04-25'),
        
        ('RVM-KLANG-005', '2026-04-03', 'Major Repair', 'Tech Robert', 
         'Compressor motor replacement', 'Compressor Motor', 850.00, 6, 
         'in_progress', 'Waiting for additional parts', '2026-05-03'),
        
        ('RVM-PETALING-006', '2026-03-30', 'Display Repair', 'Tech Lisa', 
         'Fixed touchscreen display', 'Touchscreen Panel', 420.00, 4, 
         'completed', 'Display fully functional', '2026-04-30')
    ]
    
    cursor.executemany('''
        INSERT INTO rvm_maintenance 
        (rvm_id, maintenance_date, maintenance_type, technician, 
         description, parts_replaced, cost, duration_hours, 
         status, notes, next_maintenance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', maintenance_records)
    
    print(f"✅ Inserted {len(maintenance_records)} sample maintenance records")

def insert_sample_metrics(cursor, conn):
    """Insert sample performance metrics"""
    print("\n=== Inserting sample performance metrics ===")
    
    rvm_ids = ['RVM-BANTING-001', 'RVM-PUCHONG-002', 'RVM-SUBANG-003', 
               'RVM-SHAHALAM-004', 'RVM-PETALING-006']
    
    metrics = []
    today = datetime.now()
    
    for i, rvm_id in enumerate(rvm_ids):
        for j in range(30):  # Last 30 days
            metric_date = (today - timedelta(days=j)).strftime('%Y-%m-%d')
            
            # Vary metrics based on RVM and day
            daily_collection = 80 + (i * 15) - (j % 7 * 10)
            daily_customers = 25 + (i * 5) - (j % 7 * 3)
            daily_points = int(daily_collection * (1 + i * 0.2))
            uptime = 98.5 - (j % 30 * 0.1)
            collection_time = 45 + (i * 5)
            satisfaction = 4.5 + (i * 0.1) - (j % 7 * 0.05)
            
            metrics.append((
                rvm_id,
                metric_date,
                max(10, daily_collection),
                max(5, daily_customers),
                max(50, daily_points),
                max(90, uptime),
                collection_time,
                min(5.0, max(3.0, satisfaction)),
                f"Daily metrics for {metric_date}"
            ))
    
    cursor.executemany('''
        INSERT INTO rvm_metrics 
        (rvm_id, metric_date, daily_collection_kg, daily_customers, 
         daily_rewards_points, uptime_percentage, avg_collection_time_minutes, 
         customer_satisfaction_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', metrics)
    
    print(f"✅ Inserted {len(metrics)} sample performance metrics")

def insert_sample_alerts(cursor, conn):
    """Insert sample alerts"""
    print("\n=== Inserting sample alerts ===")
    
    alerts = [
        ('RVM-BANTING-001', 'Capacity Full', 'warning', 
         'RVM at 95% capacity - Schedule cleaning soon', '2026-04-05 14:30:00',
         None, None, None, 'active'),
        
        ('RVM-PUCHONG-002', 'Low Collection', 'info', 
         'Daily collection below average for 3 consecutive days', '2026-04-04 10:15:00',
         '2026-04-04 16:00:00', 'Manager Sarah', 'Investigated - Weekend effect', 'resolved'),
        
        ('RVM-SUBANG-003', 'High Traffic', 'info', 
         'Record high customer traffic - Consider adding capacity', '2026-04-03 11:45:00',
         None, None, None, 'active'),
        
        ('RVM-KLANG-005', 'Maintenance Required', 'critical', 
         'Compressor failure - Machine offline', '2026-04-03 09:20:00',
         None, None, None, 'active'),
        
        ('RVM-PETALING-006', 'Rewards System', 'info', 
         'High rewards redemption rate - Consider adjusting points', '2026-04-02 15:30:00',
         '2026-04-03 10:00:00', 'Manager Lisa', 'Points adjusted based on analysis', 'resolved')
    ]