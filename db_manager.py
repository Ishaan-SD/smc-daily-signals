import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="smc_tracker.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Watchlist Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                ticker TEXT PRIMARY KEY,
                asset_class TEXT
            )
        ''')
        # Signals Table (The Calendar)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                ticker TEXT,
                signal_type TEXT,
                price REAL
            )
        ''')
        self.conn.commit()

    def add_ticker(self, ticker: str, asset_class: str):
        try:
            self.conn.execute("INSERT INTO watchlist (ticker, asset_class) VALUES (?, ?)", (ticker, asset_class))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Ticker already exists

    def remove_ticker(self, ticker: str):
        self.conn.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))
        self.conn.commit()

    def get_watchlist(self) -> list:
        cursor = self.conn.execute("SELECT ticker FROM watchlist")
        return [row[0] for row in cursor.fetchall()]

    def save_signals(self, signals: list):
        for sig in signals:
            self.conn.execute(
                "INSERT INTO signal_history (date, ticker, signal_type, price) VALUES (?, ?, ?, ?)",
                (sig['date'], sig['ticker'], sig['signal_type'], sig['price'])
            )
        self.conn.commit()

    def get_signal_history(self) -> pd.DataFrame:
        query = "SELECT date, ticker, signal_type, price FROM signal_history ORDER BY date DESC"
        return pd.read_sql_query(query, self.conn)