import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    def __init__(self):
        self.sender_email = os.environ.get('SENDER_EMAIL')
        self.sender_password = os.environ.get('SENDER_PASSWORD')
        self.receiver_email = os.environ.get('RECEIVER_EMAIL')
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials not found in environment variables.")

    def send_summary(self, signals: list, interval: str = "1d"):
        """
        Dispatches a single consolidated HTML email alert for all triggered signals.
        """
        if not signals:
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"📈 SMC Market Scan: {len(signals)} Signals Detected ({interval})"
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        # Build the HTML body
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>📈 Daily SMC Market Scan ({interval})</h2>
            <p>The following technical signals were detected at market close:</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
              <tr style="background-color: #f2f2f2;">
                <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Ticker</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Signal Type</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Close Price</th>
                <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Action</th>
              </tr>
        """

        for alert in signals:
            ticker = alert["ticker"]
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

            # Add row to HTML table
            html_content += f"""
              <tr>
                <td style="padding: 12px; border: 1px solid #ddd;"><strong>{display_ticker}</strong></td>
                <td style="padding: 12px; border: 1px solid #ddd;">{signal_type}</td>
                <td style="padding: 12px; border: 1px solid #ddd;">{currency_symbol}{close_price:.2f}</td>
                <td style="padding: 12px; border: 1px solid #ddd; text-align: center;">
                  <a href="{tv_link}" style="background-color: #2962FF; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Chart</a>
                </td>
              </tr>
            """

        html_content += """
            </table>
            <p style="margin-top: 30px; font-size: 12px; color: #888;">Automated by your Quantitative Trading Backend.</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            # Connect to Gmail's SMTP server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls() # Secure the connection
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            print("[SUCCESS] Consolidated Email alert sent!")
        except Exception as e:
            print(f"[ERROR] Failed to send Email alert. Details: {e}")