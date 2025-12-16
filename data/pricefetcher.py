
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

class PriceFetcher:
    def __init__(self, retry_count=3, retry_delay=2):
        self.retry_count = retry_count
        self.retry_delay = retry_delay
    
    def fetch_price_data(self, ticker, period="1y"):
        for attempt in range(self.retry_count):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=period)
                if hist.empty:
                    return {"error": "No price data available"}
                
                current_price = hist["Close"].iloc[-1]
                return {
                    "current_price": float(current_price),
                    "high_52w": float(hist["High"].max()),
                    "low_52w": float(hist["Low"].min()),
                    "volume_avg": float(hist["Volume"].mean()),
                    "last_updated": datetime.now().isoformat()
                }
            except Exception as e:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    continue
                return {"error": str(e)}
    
    def fetch_fundamentals(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "company_name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "forward_pe": info.get("forwardPE", None),
                "peg_ratio": info.get("pegRatio", None),
                "pb_ratio": info.get("priceToBook", None),
                "dividend_yield": info.get("dividendYield", None),
                "roe": info.get("returnOnEquity", None),
                "debt_to_equity": info.get("debtToEquity", None),
                "profit_margin": info.get("profitMargins", None),
                "revenue_growth": info.get("revenueGrowth", None)
            }
        except Exception as e:
            return {"error": str(e)}
