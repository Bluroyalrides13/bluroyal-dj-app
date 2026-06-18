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

        # Info product applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS info_product_applications (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                instagram_handle TEXT NOT NULL,
                audience_size TEXT,
                monthly_revenue TEXT,
                biggest_goal TEXT,
                biggest_block TEXT,
                budget_range TEXT,
                interested_offer TEXT,
                overall_score REAL,
                recommended_offer TEXT,
                status TEXT DEFAULT 'nurture',
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
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

    def create_info_product_application(self, application_data: dict) -> str:
        """Persist an info product application"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO info_product_applications (
                id, name, email, instagram_handle, audience_size, monthly_revenue,
                biggest_goal, biggest_block, budget_range, interested_offer,
                overall_score, recommended_offer, status, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            application_data.get('id'),
            application_data.get('name'),
            application_data.get('email'),
            application_data.get('instagram_handle'),
            application_data.get('audience_size'),
            application_data.get('monthly_revenue'),
            application_data.get('biggest_goal'),
            application_data.get('biggest_block'),
            application_data.get('budget_range'),
            application_data.get('interested_offer'),
            application_data.get('overall_score', 0),
            application_data.get('recommended_offer'),
            application_data.get('status', 'nurture'),
            application_data.get('notes'),
            application_data.get('created_at', datetime.utcnow().isoformat()),
            application_data.get('updated_at', datetime.utcnow().isoformat()),
        ))

        conn.commit()
        conn.close()
        return application_data.get('id')

    def get_recent_info_product_applications(self, limit: int = 20) -> List[dict]:
        """Return recent info product applications"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM info_product_applications ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    def count_info_product_applications(self) -> int:
        """Return total number of info product applications."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM info_product_applications")
        count = cursor.fetchone()[0]
        conn.close()
        return int(count)

    def get_info_product_application(self, application_id: str) -> Optional[dict]:
        """Return one info product application by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM info_product_applications WHERE id = ?",
            (application_id,),
        )
        row = cursor.fetchone()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        conn.close()

        if not row:
            return None

        return dict(zip(columns, row))

    def update_info_product_application(self, application_id: str, updates: dict) -> Optional[dict]:
        """Update one info product application and return the updated row."""
        if not updates:
            return self.get_info_product_application(application_id)

        allowed_fields = {"status", "notes", "recommended_offer", "overall_score"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
        if not filtered_updates:
            return self.get_info_product_application(application_id)

        filtered_updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{key} = ?" for key in filtered_updates.keys())
        values = list(filtered_updates.values()) + [application_id]

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE info_product_applications SET {set_clause} WHERE id = ?",
            values,
        )
        updated_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if updated_rows == 0:
            return None

        return self.get_info_product_application(application_id)
