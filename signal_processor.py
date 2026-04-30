import pandas as pd
import numpy as np

class SignalProcessor:
    def __init__(self, fvg_threshold=0.0):
        # fvg_threshold represents the barDeltaPercent filter from LuxAlgo
        self.fvg_threshold = fvg_threshold 

    def calculate_atr(self, df: pd.DataFrame, length=200) -> pd.Series:
        """Calculates Average True Range (ATR) used in LuxAlgo's volatility filters."""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(length).mean()

    def detect_bullish_fvg(self, df: pd.DataFrame) -> pd.Series:
        """
        Translates the LuxAlgo Bullish FVG logic.
        Condition: Current Low > High 2 bars ago AND Close > High 2 bars ago.
        """
        last_2_high = df['High'].shift(2)
        last_close = df['Close'].shift(1)
        last_open = df['Open'].shift(1)
        
        # Calculate Bar Delta Percent as defined in LuxAlgo
        bar_delta_percent = (last_close - last_open) / (last_open * 100)
        
        fvg_condition = (
            (df['Low'] > last_2_high) & 
            (df['Close'] > last_2_high) & 
            (bar_delta_percent > self.fvg_threshold)
        )
        return fvg_condition

    def detect_bullish_order_block(self, df: pd.DataFrame, swing_length=5) -> pd.Series:
        """
        Identifies a Bullish Order Block (The "Blue Box").
        Simplified Vectorized Logic: Finds recent swing lows followed by a strong bullish break.
        """
        # Find rolling minimums to establish swing lows
        df['Swing_Low'] = df['Low'] == df['Low'].rolling(window=swing_length, center=True).min()
        
        # Identify bearish candles (down candles)
        df['Bearish_Candle'] = df['Close'] < df['Open']
        
        # A bullish order block candidate is the last bearish candle at a swing low
        df['Bullish_OB_Candidate'] = df['Swing_Low'] & df['Bearish_Candle']
        
        return df['Bullish_OB_Candidate']

    def generate_signals(self, stock_data_dict: dict) -> list:
        """
        Scans the dictionary of DataFrames and returns a list of actionable alerts
        based on the End-of-Day (EOD) closed candle.
        """
        alerts = []
        
        for ticker, df in stock_data_dict.items():
            if df.empty or len(df) < 5:
                continue
                
            df['Bullish_FVG'] = self.detect_bullish_fvg(df)
            df['Bullish_OB'] = self.detect_bullish_order_block(df)
            
            # Reverted to iloc[-1]. Since we run this EOD, index -1 is the completed daily candle.
            latest_data = df.iloc[-1] 
            
            # Format timestamp for daily charts (no hours/minutes needed)
            latest_time = df.index[-1].strftime('%Y-%m-%d')
            close_price = latest_data['Close']
            
            if latest_data['Bullish_OB']:
                alerts.append({
                    "ticker": ticker,
                    "date": latest_time,
                    "price": close_price,
                    "signal_type": "🟦 Bullish Order Block"
                })
            elif latest_data['Bullish_FVG']:
                alerts.append({
                    "ticker": ticker,
                    "date": latest_time,
                    "price": close_price,
                    "signal_type": "🟩 Bullish Fair Value Gap"
                })
                
        return alerts