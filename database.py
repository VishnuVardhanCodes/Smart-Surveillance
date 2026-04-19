import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='database/surveillance.db'):
        self.db_path = db_path
        self._init_db()
        self._migrate_db()

    def _init_db(self):
        """Initialize the database and create tables if they don't exist."""
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                object_type TEXT NOT NULL,
                event_type TEXT DEFAULT 'Entry',
                track_id INTEGER,
                plate_number TEXT,
                image_path TEXT NOT NULL,
                camera_name TEXT DEFAULT 'Main'
            )
        ''')
        
        # Night Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS night_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                object_type TEXT NOT NULL,
                plate_number TEXT,
                image_path TEXT NOT NULL,
                camera_name TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def _migrate_db(self):
        """Handle schema migrations to ensure existing databases are up to date."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Fetch current column names
        cursor.execute("PRAGMA table_info(detections)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'event_type' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN event_type TEXT DEFAULT 'Entry'")
            
        if 'track_id' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN track_id INTEGER")
            
        if 'plate_number' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN plate_number TEXT")

        if 'camera_name' not in columns:
            cursor.execute("ALTER TABLE detections ADD COLUMN camera_name TEXT DEFAULT 'Main'")
            
        conn.commit()
        conn.close()

    def insert_detection(self, object_type, image_path, event_type='Entry', track_id=None, plate_number=None, camera_name='Main'):
        """Insert a new detection record."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (date, time, object_type, event_type, track_id, plate_number, image_path, camera_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, time_str, object_type, event_type, track_id, plate_number, image_path, camera_name))
        conn.commit()
        conn.close()
        return True

    def insert_night_alert(self, object_type, image_path, plate_number=None, camera_name='Main'):
        """Insert a night alert record."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO night_alerts (date, time, object_type, plate_number, image_path, camera_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date_str, time_str, object_type, plate_number, image_path, camera_name))
        conn.commit()
        conn.close()
        return True

    def get_all_detections(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM detections ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_recent_night_alerts(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM night_alerts ORDER BY id DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_detections_by_category(self, categories):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        placeholders = ', '.join(['?'] * len(categories))
        query = f'SELECT * FROM detections WHERE object_type IN ({placeholders}) ORDER BY id DESC'
        cursor.execute(query, categories)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_stats_for_report(self, date_str):
        """Fetch statistics for a specific date for PDF reporting."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM detections WHERE date = ? AND event_type = 'Entry'", (date_str,))
        entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detections WHERE date = ? AND event_type = 'Exit'", (date_str,))
        exits = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detections WHERE date = ? AND object_type IN ('car', 'bus', 'truck', 'motorcycle')", (date_str,))
        vehicles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT plate_number) FROM detections WHERE date = ? AND plate_number IS NOT NULL", (date_str,))
        unique_plates = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM night_alerts WHERE date = ?", (date_str,))
        night_alerts = cursor.fetchone()[0]
        
        # Hourly activity
        cursor.execute("""
            SELECT substr(time, 1, 2) as hour, COUNT(*) as count 
            FROM detections 
            WHERE date = ? 
            GROUP BY hour
        """, (date_str,))
        hourly_data = {row['hour']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        return {
            'entries': entries,
            'exits': exits,
            'vehicles': vehicles,
            'unique_plates': unique_plates,
            'night_alerts': night_alerts,
            'hourly_data': hourly_data
        }

    def get_global_stats(self):
        """Fetch total statistics for the global dashboard."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM detections WHERE event_type = 'Entry'")
        entries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detections WHERE event_type = 'Exit'")
        exits = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detections WHERE object_type IN ('car', 'bus', 'truck', 'motorcycle')")
        vehicles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM night_alerts")
        night_alerts = cursor.fetchone()[0]
        
        conn.close()
        return {
            'entries': entries,
            'exits': exits,
            'vehicles': vehicles,
            'night_alerts': night_alerts
        }

    def search_detections(self, date=None, time=None, plate_number=None, camera_name=None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM detections WHERE 1=1"
        params = []
        
        if date:
            query += " AND date = ?"
            params.append(date)
        if time:
            query += " AND time LIKE ?"
            params.append(f"%{time}%")
        if plate_number:
            query += " AND plate_number LIKE ?"
            params.append(f"%{plate_number}%")
        if camera_name:
            query += " AND camera_name = ?"
            params.append(camera_name)
            
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
