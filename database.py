import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='database/surveillance.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database and create the detections table if it doesn't exist."""
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                object_type TEXT NOT NULL,
                plate_number TEXT,
                image_path TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def insert_detection(self, object_type, image_path, plate_number=None):
        """Insert a new detection record into the database."""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (date, time, object_type, plate_number, image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, time_str, object_type, plate_number, image_path))
        conn.commit()
        conn.close()
        return True

    def get_all_detections(self):
        """Fetch all detection records."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM detections ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_detections(self, date=None, time=None, plate_number=None):
        """Search detections with filters."""
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
            
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
