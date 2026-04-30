from data_fetcher import DataFetcher
from signal_processor import SignalProcessor
from notifier import WhatsAppNotifier

# Top 20 Cryptocurrencies (Yahoo Finance Format)
CRYPTO_TICKERS = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", 
    "ADA-USD", "AVAX-USD", "DOGE-USD", "DOT-USD", "LINK-USD",
    "MATIC-USD", "SHIB-USD", "LTC-USD", "BCH-USD", "UNI7083-USD"
]

# NIFTY 50 Indian Stocks (NSE Format)
NSE_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", 
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "TITAN.NS"
]

# Combine both lists for the scanner
ALL_TICKERS = CRYPTO_TICKERS + NSE_TICKERS

def run_daily_market_scan():
    print(f"Initiating Daily Scan for {len(ALL_TICKERS)} Assets...")
    
    # 1. Fetch Data
    fetcher = DataFetcher(tickers=ALL_TICKERS)
    market_data = fetcher.fetch_data(period="1y", interval="1d")
    
    # 2. Process Signals
    processor = SignalProcessor()
    active_signals = processor.generate_signals(market_data)
    
    # 3. Dispatch Alerts
    if not active_signals:
        print("[INFO] No Smart Money Concept signals detected today.")
        return

    print(f"[INFO] Found {len(active_signals)} signals! Dispatching consolidated WhatsApp message...")
    
    notifier = WhatsAppNotifier()
    # Pass the entire list at once
    notifier.send_summary(signals=active_signals, interval="1d")

if __name__ == "__main__":
    run_daily_market_scan()