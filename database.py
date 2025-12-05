import os
from datetime import datetime

# Detect environment and set up appropriate database
DATABASE_URL = os.getenv('DATABASE_URL')
IS_VERCEL = DATABASE_URL is not None

if IS_VERCEL:
    # Use PostgreSQL on Vercel
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_db_connection():
        """Get PostgreSQL connection for Vercel"""
        return psycopg2.connect(DATABASE_URL)
else:
    # Use SQLite for local development
    import sqlite3
    
    DB_PATH = 'bookings.db'
    
    def get_db_connection():
        """Get SQLite connection for local development"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_VERCEL:
            # PostgreSQL syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    ae_name VARCHAR(255) NOT NULL,
                    ae_email VARCHAR(255) NOT NULL,
                    booking_date VARCHAR(50) NOT NULL,
                    time_slot VARCHAR(50) NOT NULL,
                    volume INTEGER NOT NULL,
                    service VARCHAR(100) NOT NULL,
                    team VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignment_counts (
                    ae_name VARCHAR(255) PRIMARY KEY,
                    team VARCHAR(50) NOT NULL,
                    assignment_count INTEGER DEFAULT 0
                )
            ''')
        else:
            # SQLite syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ae_name TEXT NOT NULL,
                    ae_email TEXT NOT NULL,
                    booking_date TEXT NOT NULL,
                    time_slot TEXT NOT NULL,
                    volume INTEGER NOT NULL,
                    service TEXT NOT NULL,
                    team TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignment_counts (
                    ae_name TEXT PRIMARY KEY,
                    team TEXT NOT NULL,
                    assignment_count INTEGER DEFAULT 0
                )
            ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized successfully ({'PostgreSQL' if IS_VERCEL else 'SQLite'})")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def get_assignment_counts(team_name):
    """Get assignment counts for a specific team"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_VERCEL:
            cursor.execute('''
                SELECT ae_name, assignment_count 
                FROM assignment_counts 
                WHERE team = %s
            ''', (team_name,))
        else:
            cursor.execute('''
                SELECT ae_name, assignment_count 
                FROM assignment_counts 
                WHERE team = ?
            ''', (team_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary
        if IS_VERCEL:
            return {row['ae_name']: row['assignment_count'] for row in results}
        else:
            return {row[0]: row[1] for row in results}
    except Exception as e:
        print(f"Error getting assignment counts: {e}")
        return {}

def initialize_team_members(team_members, team_name):
    """Initialize team members in the database if not present"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for member in team_members:
            if IS_VERCEL:
                cursor.execute('''
                    INSERT INTO assignment_counts (ae_name, team, assignment_count)
                    VALUES (%s, %s, 0)
                    ON CONFLICT (ae_name) DO NOTHING
                ''', (member['name'], team_name))
            else:
                cursor.execute('''
                    INSERT OR IGNORE INTO assignment_counts (ae_name, team, assignment_count)
                    VALUES (?, ?, 0)
                ''', (member['name'], team_name))
        
        conn.commit()
        conn.close()
        print(f"✅ Initialized {len(team_members)} members for team {team_name}")
    except Exception as e:
        print(f"Error initializing team members: {e}")

def increment_assignment_count(ae_name):
    """Increment assignment count for a specific AE"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_VERCEL:
            cursor.execute('''
                UPDATE assignment_counts 
                SET assignment_count = assignment_count + 1 
                WHERE ae_name = %s
            ''', (ae_name,))
        else:
            cursor.execute('''
                UPDATE assignment_counts 
                SET assignment_count = assignment_count + 1 
                WHERE ae_name = ?
            ''', (ae_name,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error incrementing assignment count: {e}")

def record_booking(ae_name, ae_email, booking_date, time_slot, volume, service, team):
    """Record a confirmed booking and increment assignment count"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_VERCEL:
            cursor.execute('''
                INSERT INTO bookings (ae_name, ae_email, booking_date, time_slot, volume, service, team)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (ae_name, ae_email, booking_date, time_slot, volume, service, team))
        else:
            cursor.execute('''
                INSERT INTO bookings (ae_name, ae_email, booking_date, time_slot, volume, service, team)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ae_name, ae_email, booking_date, time_slot, volume, service, team))
        
        conn.commit()
        conn.close()
        
        # Increment assignment count
        increment_assignment_count(ae_name)
        print(f"✅ Booking recorded for {ae_name}")
    except Exception as e:
        print(f"Error recording booking: {e}")

def get_all_bookings():
    """Get all bookings from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, ae_name, ae_email, booking_date, time_slot, volume, service, team, created_at
            FROM bookings
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error getting bookings: {e}")
        return []
