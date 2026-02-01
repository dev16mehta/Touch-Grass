"""SQLite database connection and schema management for place storage"""
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

# Database file path - stored in backend directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'places.db')


def get_connection():
    """Get a database connection with row factory enabled"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Create places table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS places (
                place_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                google_type TEXT,
                address TEXT,
                rating REAL,
                user_ratings_total INTEGER,
                categorization_source TEXT DEFAULT 'static',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create place_vibes many-to-many table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS place_vibes (
                place_id TEXT,
                vibe TEXT,
                PRIMARY KEY (place_id, vibe),
                FOREIGN KEY (place_id) REFERENCES places(place_id) ON DELETE CASCADE
            )
        ''')

        # Create indexed_areas table to track which areas have been fetched
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indexed_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                center_lat REAL NOT NULL,
                center_lon REAL NOT NULL,
                radius REAL NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for efficient queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_vibes_vibe ON place_vibes(vibe)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_location ON places(latitude, longitude)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_indexed_areas_location ON indexed_areas(center_lat, center_lon)')


# Initialize database on module import
init_db()
