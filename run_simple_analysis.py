#!/usr/bin/env python3
"""Simple NSE analysis runner without complex dependencies"""

import sys
import os
import time
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.pricefetcher import PriceFetcher
from data.technicalcalculator import TechnicalCalculator
import yfinance as yf
import pandas as pd

class SimpleNSEAnalyzer:
    def __init__(self):
        self.fetcher = PriceFetcher()
        self.tech_calc = TechnicalCalculator()
        
    def load_nse_stocks(self, limit=None, priority_only=False):
        """Load NSE stocks from clean CSV"""
        clean_file = '/home/sagemaker-user/stock-analysis/data/nse_stocks_clean.csv'
        df = pd.read_csv(clean_file)
        
        if priority_only:
            df = df[df['group'] == 'A']
        
        if limit:
            df = df.head(limit)
        
        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                'ticker': f"{row['security_id']}.NS",
                'name': row['issuer_name'],
                'symbol': row['security_id'],
                'group': row['group']
            })
        
        return stocks
    
    def analyze_stock(self, stock):
        """Analyze a single stock"""
        ticker = stock['ticker']
        
        try:
            # Get price data
            price_data = self.fetcher.fetch_price_data(ticker)
            if "error" in price_data:
                return {"ticker": ticker, "status": "failed", "error": price_data["error"]}
            
            # Get fundamentals
            fundamentals = self.fetcher.fetch_fundamentals(ticker)
            
            # Get technical indicators
            hist = yf.Ticker(ticker).history(period="6mo")
            technical_indicators = {}
            if not hist.empty and len(hist) >= 50:
                technical_indicators = self.tech_calc.calculate_indicators(hist)
            
            # Simple scoring
            score = self.calculate_simple_score(price_data, fundamentals, technical_indicators)
            
            return {
                "ticker": ticker,
                "name": stock['name'],
                "group": stock['group'],
                "status": "success",
                "price_data": price_data,
                "fundamentals": fundamentals,
                "technical": technical_indicators,
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"ticker": ticker, "status": "error", "error": str(e)}
    
    def calculate_simple_score(self, price_data, fundamentals, technical):
        """Calculate a simple investment score"""
        score = 0.5  # Neutral starting point
        
        try:
            # Technical scoring
            if technical.get('rsi14'):
                rsi = technical['rsi14']
                if 30 <= rsi <= 70:  # Good RSI range
                    score += 0.1
                elif rsi < 30:  # Oversold - potential buy
                    score += 0.2
                elif rsi > 80:  # Overbought - caution
                    score -= 0.1
            
            # Price vs moving averages
            current_price = price_data.get('current_price', 0)
            sma20 = technical.get('sma20', 0)
            sma50 = technical.get('sma50', 0)
            
            if current_price > sma20 > sma50:  # Uptrend
                score += 0.15
            elif current_price < sma20 < sma50:  # Downtrend
                score -= 0.1
            
            # Fundamental scoring
            pe_ratio = fundamentals.get('pe_ratio')
            if pe_ratio and 10 <= pe_ratio <= 25:  # Reasonable P/E
                score += 0.1
            
            # Market cap consideration
            market_cap = fundamentals.get('market_cap', 0)
            if market_cap > 100000000000:  # Large cap (>1000 Cr)
                score += 0.05
            
        except Exception:
            pass
        
        return max(0, min(1, score))  # Clamp between 0 and 1
    
    def get_recommendation(self, score):
        """Get recommendation based on score"""
        if score >= 0.7:
            return "BUY"
        elif score >= 0.6:
            return "HOLD"
        elif score >= 0.4:
            return "NEUTRAL"
        else:
            return "SELL"
    
    def process_stocks(self, stocks):
        """Process multiple stocks"""
        results = []
        
        print(f"Processing {len(stocks)} stocks...")
        
        for i, stock in enumerate(stocks, 1):
            print(f"[{i}/{len(stocks)}] Analyzing {stock['ticker']} ({stock['name']})...")
            
            result = self.analyze_stock(stock)
            results.append(result)
            
            if result['status'] == 'success':
                score = result['score']
                recommendation = self.get_recommendation(score)
                price = result['price_data']['current_price']
                print(f"  ✅ Price: ₹{price:.2f} | Score: {score:.2f} | {recommendation}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Rate limiting
            time.sleep(1)
        
        return results
    
    def save_results(self, results, filename):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_simple_analysis.py <command> [count]")
        print("Commands:")
        print("  test [count]    - Test with limited stocks (default: 5)")
        print("  priority [count] - Process Group A stocks (default: 20)")
        print("  sample [count]  - Process sample stocks (default: 50)")
        return
    
    command = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    analyzer = SimpleNSEAnalyzer()
    
    if command == "test":
        count = count or 5
        stocks = analyzer.load_nse_stocks(limit=count)
        results = analyzer.process_stocks(stocks)
        analyzer.save_results(results, f"test_results_{count}stocks.json")
        
    elif command == "priority":
        count = count or 20
        stocks = analyzer.load_nse_stocks(limit=count, priority_only=True)
        results = analyzer.process_stocks(stocks)
        analyzer.save_results(results, f"priority_results_{count}stocks.json")
        
    elif command == "sample":
        count = count or 50
        stocks = analyzer.load_nse_stocks(limit=count)
        results = analyzer.process_stocks(stocks)
        analyzer.save_results(results, f"sample_results_{count}stocks.json")
        
    else:
        print(f"Unknown command: {command}")
        return
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n=== Summary ===")
    print(f"Processed: {successful}/{len(results)} stocks")
    
    if successful > 0:
        # Show top recommendations
        success_results = [r for r in results if r['status'] == 'success']
        success_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nTop 5 recommendations:")
        for i, result in enumerate(success_results[:5], 1):
            score = result['score']
            recommendation = analyzer.get_recommendation(score)
            price = result['price_data']['current_price']
            print(f"  {i}. {result['ticker']} - {recommendation} (Score: {score:.2f}, Price: ₹{price:.2f})")

if __name__ == "__main__":
    main()