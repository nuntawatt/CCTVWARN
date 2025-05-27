# db.py - Database handling for person detection system

import sqlite3
import os
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# 🔐 Firebase setup
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
firebase_db = firestore.client()

class Database:
    def __init__(self, db_path):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def _connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()

    def _disconnect(self):
        """Disconnect from the database"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def initialize(self):
        """Initialize database tables"""
        self._connect()

        # Create detections table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT,
            created_at TEXT NOT NULL
        )
        ''')

        # Create index for faster queries
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_camera_timestamp ON detections (camera_id, timestamp)')

        self.conn.commit()
        self._disconnect()

    def add_detection(self, camera_id, timestamp, confidence, image_path=""):
        """Add a new detection to SQLite and Firebase"""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to SQLite
        self._connect()
        self.cursor.execute('''
        INSERT INTO detections (camera_id, timestamp, confidence, image_path, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (camera_id, timestamp, confidence, image_path, created_at))
        self.conn.commit()
        self._disconnect()

        # Send to Firebase
        try:
            firebase_db.collection("detections").add({
                "camera_id": camera_id,
                "timestamp": timestamp,
                "confidence": confidence,
                "image_path": image_path,
                "created_at": created_at
            })
        except Exception as e:
            print("[Firebase Error]", e)

    def get_recent_detections(self, camera_id, limit=10):
        """Get recent detections for a specific camera"""
        self._connect()
        self.cursor.execute('''
        SELECT id, camera_id, timestamp, confidence, image_path 
        FROM detections 
        WHERE camera_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        ''', (camera_id, limit))
        results = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return results

    def get_recent_detections_all(self, limit=20):
        """Get recent detections for all cameras"""
        self._connect()
        self.cursor.execute('''
        SELECT id, camera_id, timestamp, confidence, image_path 
        FROM detections 
        ORDER BY timestamp DESC 
        LIMIT ?
        ''', (limit,))
        results = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return results

    def get_detection_counts(self, camera_id):
        """Get detection counts for a specific camera"""
        self._connect()
        self.cursor.execute('''
        SELECT COUNT(*) as person_count 
        FROM detections 
        WHERE camera_id = ?
        ''', (camera_id,))
        result = self.cursor.fetchone()
        count = result['person_count'] if result else 0
        self._disconnect()
        return {"person": count}

    def get_total_counts(self):
        """Get total detection counts for all cameras"""
        self._connect()
        self.cursor.execute('''
        SELECT camera_id, COUNT(*) as count 
        FROM detections 
        GROUP BY camera_id
        ''')
        results = {row['camera_id']: row['count'] for row in self.cursor.fetchall()}
        self.cursor.execute('SELECT COUNT(*) as total FROM detections')
        results['total'] = self.cursor.fetchone()['total']
        self._disconnect()
        return results

    def get_all_detections(self):
        """Get all detections for export"""
        self._connect()
        self.cursor.execute('''
        SELECT id, camera_id, timestamp, confidence, image_path 
        FROM detections 
        ORDER BY timestamp DESC
        ''')
        results = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return results

    def get_detections_by_date(self, date):
        """Get detections for a specific date (YYYY-MM-DD)"""
        self._connect()
        date_pattern = f"{date}%"
        self.cursor.execute('''
        SELECT id, camera_id, timestamp, confidence, image_path 
        FROM detections 
        WHERE timestamp LIKE ? 
        ORDER BY timestamp DESC
        ''', (date_pattern,))
        results = [dict(row) for row in self.cursor.fetchall()]
        self._disconnect()
        return results

    def delete_old_detections(self, days=30):
        """Delete detections older than specified days"""
        self._connect()
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        self.cursor.execute('''
        DELETE FROM detections 
        WHERE timestamp < ?
        ''', (cutoff_date,))
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        self._disconnect()
        return deleted_count
