#!/usr/bin/env python3
"""
Database Initialization Script for ET AI Concierge
--------------------------------------------------
Sets up the SQLite database with required tables for first-time setup.

Run this script once before deploying the application:
    python init_database.py

This creates:
- user_memory.db with user_profiles table
- Ensures data directory exists
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialize the SQLite database with required schema."""

    # Ensure data directory exists
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / "user_memory.db"

    print(f"Initializing database at: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create user_profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            session_id TEXT PRIMARY KEY,
            profile_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_session_id
        ON user_profiles(session_id)
    ''')

    conn.commit()
    conn.close()

    print("✅ Database initialized successfully!")
    print(f"📁 Database location: {db_path}")
    print("📊 Tables created: user_profiles")
    print("\nYou can now run the application.")

if __name__ == "__main__":
    init_database()