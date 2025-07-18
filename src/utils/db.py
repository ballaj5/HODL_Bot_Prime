# src/utils/db.py
import sqlite3
import threading
import logging
from .paths import get_path # Correct relative import

logger = logging.getLogger(__name__)

DB_FILE = get_path("signals.db")
thread_local = threading.local()

def get_db_conn():
    """Gets a thread-safe database connection."""
    if not hasattr(thread_local, 'conn'):
        thread_local.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return thread_local.conn

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            symbol TEXT PRIMARY KEY,
            last_signal TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    logger.info("Database initialized successfully.")

def store_signal(symbol: str, signal: str):
    """Stores or updates a signal for a given symbol."""
    from datetime import datetime
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO signals (symbol, last_signal, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE 
              SET last_signal=excluded.last_signal, timestamp=excluded.timestamp
        """, (symbol, signal, datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to store signal for {symbol}: {e}")
        conn.rollback()

def load_last_signal(symbol: str) -> str | None:
    """Loads the last recorded signal for a symbol."""
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT last_signal FROM signals WHERE symbol = ?", (symbol,))
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        logger.error(f"Failed to load signal for {symbol}: {e}")
        return None

def should_alert(symbol: str, new_signal: str) -> bool:
    """Checks if a new signal is different from the last recorded one."""
    last = load_last_signal(symbol)
    if last != new_signal:
        logger.info(f"🔔 New alert-worthy signal for {symbol}: {new_signal} (previously: {last})")
        return True
    return False