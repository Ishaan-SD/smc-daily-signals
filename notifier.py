import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv() 

class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_whatsapp_number = 'whatsapp:+14155238886' 
        self.to_whatsapp_number = os.environ.get('YOUR_WHATSAPP_NUMBER') 
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("Twilio credentials not found. Check your secrets.")

        self.client = Client(self.account_sid, self.auth_token)

    def send_summary(self, signals: list, interval: str = "1d"):
        """
        Dispatches a single consolidated WhatsApp alert for all triggered signals.
        """
        if not signals:
            return

        # Start the master message
        message_lines = [f"📈 *DAILY SMC MARKET SCAN ({interval})* 📈\n"]

        for alert in signals:
            ticker = alert["ticker"]
            date = alert["date"]
            close_price = alert["price"]
            signal_type = alert["signal_type"]

            # Dynamic Formatting
            currency_symbol = "$"
            if ticker.endswith(".NS"):
                tv_symbol = f"NSE:{ticker.replace('.NS', '')}"
                display_ticker = ticker.replace('.NS', '')
                currency_symbol = "₹"
            elif ticker.endswith(".BO"):
                tv_symbol = f"BSE:{ticker.replace('.BO', '')}"
                display_ticker = ticker.replace('.BO', '')
                currency_symbol = "₹"
            elif ticker.endswith("-USD"):
                tv_symbol = f"CRYPTO:{ticker.replace('-', '')}"
                display_ticker = ticker
                currency_symbol = "$"
            else:
                tv_symbol = ticker
                display_ticker = ticker

            tv_interval_map = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "1d": "D"}
            tv_interval = tv_interval_map.get(interval, "1")
            tv_link = f"https://www.tradingview.com/chart/?symbol={tv_symbol}&interval={tv_interval}"

            # Append each signal to the master message
            message_lines.append(
                f"🔹 *{display_ticker}* | {signal_type}\n"
                f"Price: {currency_symbol}{close_price:.2f}\n"
                f"Chart: {tv_link}\n"
            )

        # Join all lines together into one block of text
        message_body = "\n".join(message_lines)

        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_whatsapp_number,
                to=self.to_whatsapp_number
            )
            print(f"[SUCCESS] Consolidated alert sent! SID: {message.sid}")
        except Exception as e:
            print(f"[ERROR] Failed to send consolidated alert. Details: {e}")