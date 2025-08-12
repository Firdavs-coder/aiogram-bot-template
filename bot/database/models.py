# Direct SQL for users table creation using sqlite3
import sqlite3

def create_users_table(conn):
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY UNIQUE
            )
        ''')