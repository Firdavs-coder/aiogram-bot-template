import sqlite3
from datetime import datetime
from typing import Optional


class User:
    """User model for database operations"""
    
    def __init__(self, user_id: int, name: str, date: Optional[str] = None):
        self.id = user_id
        self.name = name
        self.date = date or datetime.utcnow().isoformat()

    @staticmethod
    def create_table(conn: sqlite3.Connection) -> None:
        """Create users table if it doesn't exist"""
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY UNIQUE,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

    def save(self, conn: sqlite3.Connection) -> None:
        """Save or update user in database"""
        with conn:
            conn.execute('''
                INSERT INTO users (id, name, date)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET 
                    name=excluded.name, 
                    date=excluded.date
            ''', (self.id, self.name, self.date))

    @staticmethod
    def get_by_id(conn: sqlite3.Connection, user_id: int) -> Optional['User']:
        """Get user by ID from database"""
        cursor = conn.execute(
            'SELECT id, name, date FROM users WHERE id = ?', (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2])
        return None

    @staticmethod
    def get_all(conn: sqlite3.Connection) -> list['User']:
        """Get all users from database"""
        cursor = conn.execute('SELECT id, name, date FROM users')
        return [User(row[0], row[1], row[2]) for row in cursor.fetchall()]