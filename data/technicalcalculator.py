
import pandas as pd
import numpy as np

class TechnicalCalculator:
    def calculate_indicators(self, df):
        if df.empty or len(df) < 50:
            return {}
        
        try:
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # Moving Averages
            sma20 = df['Close'].rolling(window=20).mean()
            sma50 = df['Close'].rolling(window=50).mean()
            sma200 = df['Close'].rolling(window=200).mean()
            
            # MACD
            ema12 = df['Close'].ewm(span=12).mean()
            ema26 = df['Close'].ewm(span=26).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9).mean()
            
            # Bollinger Bands
            bb_middle = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            return {
                "current_price": float(df['Close'].iloc[-1]),
                "rsi14": float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else None,
                "sma20": float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else None,
                "sma50": float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else None,
                "sma200": float(sma200.iloc[-1]) if not np.isnan(sma200.iloc[-1]) else None,
                "macd": float(macd.iloc[-1]) if not np.isnan(macd.iloc[-1]) else None,
                "macd_signal": float(signal.iloc[-1]) if not np.isnan(signal.iloc[-1]) else None,
                "bb_upper": float(bb_upper.iloc[-1]) if not np.isnan(bb_upper.iloc[-1]) else None,
                "bb_middle": float(bb_middle.iloc[-1]) if not np.isnan(bb_middle.iloc[-1]) else None,
                "bb_lower": float(bb_lower.iloc[-1]) if not np.isnan(bb_lower.iloc[-1]) else None
            }
        except Exception as e:
            return {"error": str(e)}
