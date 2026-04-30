import os
from twilio.rest import Client
from dotenv import load_dotenv

# This loads the variables from your .env file
load_dotenv() 

class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        # Twilio's default sandbox number for WhatsApp
        self.from_whatsapp_number = 'whatsapp:+14155238886' 
        
        # Your verified personal number formatted as 'whatsapp:+91...'
        self.to_whatsapp_number = os.environ.get('YOUR_WHATSAPP_NUMBER') 
        
        # Safety check to ensure environment variables are loaded
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not found. Check your .env file.")

        self.client = Client(self.account_sid, self.auth_token)

    def send_alert(self, ticker: str, date: str, close_price: float, signal_type: str, interval: str = "1m"):
        """
        Dispatches a WhatsApp alert with dynamic TradingView links for Crypto and Stocks.
        """
        # --- NEW DYNAMIC TICKER FORMATTING ---
        currency_symbol = "$"
        
        if ticker.endswith(".NS"): # Indian NSE Stocks
            tv_symbol = f"NSE:{ticker.replace('.NS', '')}"
            display_ticker = ticker.replace('.NS', '')
            currency_symbol = "₹"
            
        elif ticker.endswith(".BO"): # Indian BSE Stocks
            tv_symbol = f"BSE:{ticker.replace('.BO', '')}"
            display_ticker = ticker.replace('.BO', '')
            currency_symbol = "₹"
            
        elif ticker.endswith("-USD"): # Crypto Assets
            tv_symbol = f"CRYPTO:{ticker.replace('-', '')}" # BTC-USD -> CRYPTO:BTCUSD
            display_ticker = ticker
            currency_symbol = "$"
            
        else: # US Stocks or Fallback
            tv_symbol = ticker
            display_ticker = ticker
        # -------------------------------------

        tv_interval_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "1d": "D"}
        tv_interval = tv_interval_map.get(interval, "1")

        tv_link = f"https://www.tradingview.com/chart/?symbol={tv_symbol}&interval={tv_interval}"

        # Notice we are now using the dynamic currency_symbol variable
        message_body = (
            f"📈 *TRADING ALERT: {display_ticker}*\n"
            f"Signal: {signal_type}\n"
            f"Timeframe: {interval}\n"
            f"Candle Date: {date}\n"
            f"Close Price: {currency_symbol}{close_price:.2f}\n\n"
            f"📊 View Chart: {tv_link}"
        )

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_whatsapp_number,
                to=self.to_whatsapp_number
            )
            print(f"[SUCCESS] Alert sent for {ticker}. SID: {message.sid}")
        except Exception as e:
            print(f"[ERROR] Failed to send alert for {ticker}. Details: {e}")