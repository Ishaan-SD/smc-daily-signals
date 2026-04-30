import yfinance as yf
import pandas as pd

class DataFetcher:
    def __init__(self, tickers: list):
        self.tickers = tickers

    # Updated method signature to handle intraday intervals
    def fetch_data(self, period="1d", interval="1m") -> dict:
        stock_data = {}
        for ticker in self.tickers:
            try:
                # Swapped to use the dynamic interval parameter
                df = yf.download(ticker, period=period, interval=interval, progress=False)
                
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
                
                stock_data[ticker] = df
            except Exception as e:
                print(f"[ERROR] Failed to fetch data for {ticker}: {e}")
                
        return stock_data