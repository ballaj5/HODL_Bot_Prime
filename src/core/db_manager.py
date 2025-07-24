import sqlite3
from logger import logger

class DBManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info("Successfully connected to the database.")
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")

    def execute_query(self, query, params=()):
        """Execute a given SQL query."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                return cursor
        except sqlite3.Error as e:
            logger.error(f"Database query failed: {query} with params {params}. Error: {e}")
            # Depending on the desired behavior, you might want to reconnect or raise
            raise

    def check_for_existing_table(self, table_name):
        """Check if a table exists in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        result = self.execute_query(query, (table_name,)).fetchone()
        return result is not None

    def create_trades_table(self):
        """Create the trades table if it doesn't exist."""
        if not self.check_for_existing_table("trades"):
            query = """
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                type TEXT,
                price REAL,
                amount REAL,
                status TEXT
            );
            """
            self.execute_query(query)
            logger.info("Created 'trades' table.")

    def log_trade(self, symbol, trade_type, price, amount, status):
        """Log a trade into the database."""
        query = "INSERT INTO trades (symbol, type, price, amount, status) VALUES (?, ?, ?, ?, ?);"
        params = (symbol, trade_type, price, amount, status)
        self.execute_query(query, params)
        logger.info(f"Logged trade: {trade_type} {amount} {symbol} at {price}")