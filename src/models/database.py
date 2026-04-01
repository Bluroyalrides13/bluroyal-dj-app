"""
SQLite database models and session management
"""

import sqlite3
from typing import Optional, List
import json
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_url: str = "sqlite:///./luxury_rideshare.db"):
        """Initialize database connection"""
        # Extract file path from SQLite URL
        self.db_path = db_url.replace("sqlite:///", "")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                initial_message TEXT,
                budget_score REAL,
                frequency_score REAL,
                location_score REAL,
                preference_score REAL,
                engagement_score REAL,
                overall_score REAL,
                status TEXT DEFAULT 'new',
                conversation_summary TEXT,
                recommended_tier TEXT,
                next_steps TEXT,
                assigned_to TEXT,
                created_at TEXT,
                updated_at TEXT,
                converted_at TEXT
            )
        """)
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                preferred_service_tier TEXT,
                total_bookings INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0.0,
                average_rating REAL,
                is_vip BOOLEAN DEFAULT 0,
                created_at TEXT
            )
        """)
        
        # Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                customer_email TEXT,
                customer_phone TEXT,
                pickup_location TEXT NOT NULL,
                dropoff_location TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                passenger_count INTEGER,
                service_tier TEXT,
                special_requests TEXT,
                quote_json TEXT,
                status TEXT DEFAULT 'quoted',
                payment_id TEXT,
                confirmation_number TEXT UNIQUE,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Quotes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                service_tier TEXT,
                base_fare REAL,
                estimated_distance_miles REAL,
                distance_charge REAL,
                estimated_duration_minutes REAL,
                duration_charge REAL,
                subtotal REAL,
                tax_rate REAL,
                tax REAL,
                total_fare REAL,
                currency TEXT DEFAULT 'USD',
                valid_until TEXT,
                created_at TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            )
        """)
        
        # Conversation sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                customer_id TEXT,
                source TEXT,
                messages_json TEXT,
                extracted_data_json TEXT,
                status TEXT DEFAULT 'active',
                started_at TEXT,
                ended_at TEXT,
                escalation_reason TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                booking_id TEXT NOT NULL,
                amount_cents INTEGER,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                square_payment_id TEXT,
                receipt_url TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_lead(self, lead_data: dict) -> str:
        """Create a new lead"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO leads (
                id, source, name, email, phone, initial_message,
                budget_score, frequency_score, location_score, preference_score,
                engagement_score, overall_score, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_data.get('id'),
            lead_data.get('source'),
            lead_data.get('name'),
            lead_data.get('email'),
            lead_data.get('phone'),
            lead_data.get('initial_message'),
            lead_data.get('budget_score', 0),
            lead_data.get('frequency_score', 0),
            lead_data.get('location_score', 0),
            lead_data.get('preference_score', 0),
            lead_data.get('engagement_score', 0),
            lead_data.get('overall_score', 0),
            lead_data.get('status', 'new'),
            lead_data.get('created_at', datetime.utcnow().isoformat()),
            lead_data.get('updated_at', datetime.utcnow().isoformat()),
        ))
        
        conn.commit()
        conn.close()
        return lead_data.get('id')
    
    def update_lead(self, lead_id: str, updates: dict) -> bool:
        """Update an existing lead"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [lead_id]
        
        cursor.execute(f"UPDATE leads SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return True
    
    def get_lead(self, lead_id: str) -> Optional[dict]:
        """Get a lead by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def create_booking(self, booking_data: dict) -> str:
        """Create a new booking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bookings (
                id, customer_id, customer_email, customer_phone,
                pickup_location, dropoff_location, booking_date, booking_time,
                passenger_count, service_tier, special_requests, quote_json,
                status, confirmation_number, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            booking_data.get('id'),
            booking_data.get('customer_id'),
            booking_data.get('customer_email'),
            booking_data.get('customer_phone'),
            booking_data.get('pickup_location'),
            booking_data.get('dropoff_location'),
            booking_data.get('booking_date'),
            booking_data.get('booking_time'),
            booking_data.get('passenger_count'),
            booking_data.get('service_tier'),
            booking_data.get('special_requests'),
            json.dumps(booking_data.get('quote', {})),
            booking_data.get('status', 'quoted'),
            booking_data.get('confirmation_number'),
            booking_data.get('created_at', datetime.utcnow().isoformat()),
            booking_data.get('updated_at', datetime.utcnow().isoformat()),
        ))
        
        conn.commit()
        conn.close()
        return booking_data.get('id')
