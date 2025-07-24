# src/utils/database.py
import psycopg2
import psycopg2.extras # Needed for dictionary-like rows
import logging
import sys
import os # To get database URL from environment variables

# REMOVED: DB_PATH is no longer needed
# CHANGED: Get the database connection URL from the environment variable set in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        # CHANGED: Connect to PostgreSQL using the DATABASE_URL
        # The cursor_factory makes rows behave like dictionaries, similar to conn.row_factory in sqlite3
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initializes the database and creates the predictions table if it doesn't exist."""
    conn = get_db_connection()
    if conn is None:
        logging.error("Could not initialize database: connection failed.")
        return

    try:
        cursor = conn.cursor()
        # CHANGED: Updated table definition for PostgreSQL
        # - SERIAL PRIMARY KEY is the equivalent of AUTOINCREMENT
        # - TIMESTAMP is the equivalent of DATETIME
        # - DOUBLE PRECISION is the equivalent of REAL
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            signal TEXT NOT NULL,
            confidence DOUBLE PRECISION NOT NULL,
            price_at_prediction DOUBLE PRECISION,
            volatility DOUBLE PRECISION,
            llm_insight TEXT,
            sent_to_telegram INTEGER DEFAULT 0
        );
        """)
        conn.commit()
        logging.info("Database initialized and 'predictions' table ensured.")
    except psycopg2.Error as e:
        logging.error(f"Error initializing database table: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def save_signal(context: dict):
    """Saves a new signal/prediction to the database."""
    conn = get_db_connection()
    if conn is None:
        logging.error("Could not save signal: database connection failed.")
        return

    # CHANGED: SQL placeholder is now %s instead of ?
    sql = """
        INSERT INTO predictions (symbol, timeframe, signal, confidence, price_at_prediction, volatility, llm_insight)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            context.get('symbol'),
            context.get('timeframe'),
            context.get('signal'),
            context.get('confidence'),
            context.get('price_at_prediction'),
            context.get('volatility'),
            context.get('llm_insight')
        ))
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Failed to save signal for {context.get('symbol')}: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_live_signals(confidence_threshold: float = 70.0):
    """Fetches recent signals from the DB that meet a confidence threshold."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        # CHANGED: SQL placeholder is now %s instead of ?
        query = """
            SELECT * FROM predictions
            WHERE confidence >= %s
            ORDER BY timestamp DESC
            LIMIT 50;
        """
        cursor.execute(query, (confidence_threshold,))
        signals = cursor.fetchall()
        return signals
    except psycopg2.Error as e:
        logging.error(f"Failed to fetch live signals: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

# This function remains the same as it does not interact with the database.
def get_accuracy_stats(signal_type: str):
    """
    Placeholder function to return dummy accuracy statistics.
    """
    logging.warning(f"Returning placeholder accuracy stats for signal type: {signal_type}.")
    return {
        "24h": 0.0,
        "7d": 0.0,
        "30d": 0.0
    }

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init_db':
        init_db()