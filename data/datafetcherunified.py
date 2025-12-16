
import yfinance as yf
import asyncio
from datetime import datetime
from data.pricefetcher import PriceFetcher
from data.technicalcalculator import TechnicalCalculator

class ComprehensiveDataFetcher:
    def __init__(self):
        self.price_fetcher = PriceFetcher()
        self.tech_calculator = TechnicalCalculator()
    
    async def fetch_all_data(self, ticker):
        """Fetch all data for a stock ticker"""
        errors = []
        result = {"ticker": ticker, "timestamp": datetime.now().isoformat()}
        
        # Fetch price data
        try:
            price_data = self.price_fetcher.fetch_price_data(ticker)
            if "error" in price_data:
                errors.append(f"Price: {price_data['error']}")
            else:
                result["price"] = price_data
        except Exception as e:
            errors.append(f"Price fetch error: {str(e)}")
        
        # Fetch fundamentals
        try:
            fundamentals = self.price_fetcher.fetch_fundamentals(ticker)
            if "error" in fundamentals:
                errors.append(f"Fundamentals: {fundamentals['error']}")
            else:
                result["fundamentals"] = fundamentals
        except Exception as e:
            errors.append(f"Fundamentals error: {str(e)}")
        
        # Fetch and calculate technical indicators
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if not hist.empty:
                technical = self.tech_calculator.calculate_indicators(hist)
                if "error" in technical:
                    errors.append(f"Technical: {technical['error']}")
                else:
                    result["technical"] = technical
            else:
                errors.append("Technical: No historical data")
        except Exception as e:
            errors.append(f"Technical error: {str(e)}")
        
        if errors:
            result["errors"] = errors
        
        return result
