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

    def detect_bullish_fvg(self, df: pd.DataFrame, min_gap_percent=0.0) -> pd.Series:
        """
        Strictly translates the LuxAlgo Bullish FVG logic, with an added 
        custom quantitative filter to ignore "micro gaps".
        """
        # LuxAlgo variable mapping (3-candle sequence)
        last_2_high = df['High'].shift(2)   # High of Bar 1
        last_close = df['Close'].shift(1)   # Close of Bar 2 (The displacement candle)
        last_open = df['Open'].shift(1)     # Open of Bar 2
        
        # 1. LuxAlgo Displacement Filter (Momentum)
        bar_delta_percent = (last_close - last_open) / (last_open * 100)
        dynamic_threshold = bar_delta_percent.abs().expanding().mean() * 2
        
        # 2. NEW: Actual Gap Size Filter (Structural Width)
        # Calculates the physical gap space as a percentage of the asset's price
        actual_gap_size_percent = (df['Low'] - last_2_high) / last_2_high
        
        # 3. Exact LuxAlgo Condition + Micro-Gap Filter
        fvg_condition = (
            (df['Low'] > last_2_high) & 
            (last_close > last_2_high) & 
            (bar_delta_percent > dynamic_threshold) &
            (actual_gap_size_percent >= min_gap_percent) # <-- The new strictness rule
        )
        
        return fvg_condition
    

    def detect_bullish_order_block(self, df: pd.DataFrame, swing_length=5) -> pd.Series:
        """
        Translates LuxAlgo OB logic: OB is confirmed only when a BOS occurs.
        """
        # 1. Detect Swing Highs (Pivots)
        # LuxAlgo uses high[size] > ta.highest(size) logic
        df['is_swing_high'] = (df['High'] == df['High'].rolling(window=swing_length*2, center=True).max())
        
        # 2. Track the most recent un-broken Pivot High
        # We use ffill() to keep the "level to beat" active
        df['active_pivot_high'] = df['High'].where(df['is_swing_high']).ffill()
        
        # 3. Detect the Break of Structure (BOS)
        # LuxAlgo: ta.crossover(close, p_ivot.currentLevel)
        df['has_bos'] = (df['Close'] > df['active_pivot_high']) & (df['Close'].shift(1) <= df['active_pivot_high'].shift(1))
        
        # 4. Identify the OB candle (The Blue Box source)
        # LuxAlgo looks for the candle with the lowest 'Parsed Low' between the pivot and the break
        # For a trigger alert, we return True on the bar where 'has_bos' is True
        return df['has_bos']

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
            # uncomment below if we need to send Bullish FVG signals
            # elif latest_data['Bullish_FVG']:
            #     alerts.append({
            #         "ticker": ticker,
            #         "date": latest_time,
            #         "price": close_price,
            #         "signal_type": "🟩 Bullish Fair Value Gap"
            #     })
                
        return alerts