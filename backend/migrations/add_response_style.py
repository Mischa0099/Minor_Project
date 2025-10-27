"""Safe migration: add response_style column to Profile table for SQLite.
Run with: python migrations/add_response_style.py
This will ALTER TABLE to add a TEXT column with default 'concise' if it doesn't exist.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols

def main():
    if not os.path.exists(DB_PATH):
        print('Database not found at', DB_PATH)
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        if not column_exists(conn, 'profile', 'response_style'):
            print('Adding response_style column to profile...')
            conn.execute("ALTER TABLE profile ADD COLUMN response_style TEXT DEFAULT 'concise'")
            conn.commit()
            print('Migration applied successfully.')
        else:
            print('Column response_style already exists; no action taken.')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
