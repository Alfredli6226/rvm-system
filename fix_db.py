#!/usr/bin/env python3
"""
Fix RVM database - Insert all locations
"""

import os
import sqlite3
import json

# Database path
data_dir = os.path.join(os.path.dirname(__file__), 'data')
db_path = os.path.join(data_dir, 'rvm_management.db')

print(f"Database path: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load from JSON
json_path = os.path.join(data_dir, 'rvm_locations.json')
print(f"JSON path: {json_path}")

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rvm_locations = data['rvm_locations']
    print(f"Found {len(rvm_locations)} locations in JSON")
    
    # Insert all locations
    for location in rvm_locations:
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
    
    conn.commit()
    print(f"✅ Inserted {len(rvm_locations)} locations")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Check
cursor.execute('SELECT COUNT(*) FROM rvm_locations')
count = cursor.fetchone()[0]
print(f"Rows in rvm_locations: {count}")

cursor.execute('SELECT id, name, status FROM rvm_locations')
rows = cursor.fetchall()
print("\nAll locations:")
for row in rows:
    print(f"  {row[0]}: {row[1]} ({row[2]})")

conn.close()