#!/usr/bin/env python3
"""Test technical analysis functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_technical_analysis():
    """Test technical indicators"""
    
    from data.pricefetcher import PriceFetcher
    from data.technicalcalculator import TechnicalCalculator
    import yfinance as yf
    
    print("Testing technical analysis with INFY...")
    
    # Get historical data
    ticker = "INFY.NS"
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")  # 6 months of data
    
    if hist.empty:
        print("✗ No historical data available")
        return False
    
    print(f"✓ Got {len(hist)} days of historical data")
    
    # Test technical calculator
    tech_calc = TechnicalCalculator()
    
    try:
        # Test all indicators at once
        indicators = tech_calc.calculate_indicators(hist)
        
        if "error" in indicators:
            print(f"✗ Technical calculation failed: {indicators['error']}")
            return False
        
        print(f"✓ Current Price: ₹{indicators['current_price']:.2f}")
        
        if indicators['rsi14']:
            print(f"✓ RSI (14): {indicators['rsi14']:.2f}")
        
        if indicators['macd'] and indicators['macd_signal']:
            print(f"✓ MACD: {indicators['macd']:.4f}")
            print(f"✓ MACD Signal: {indicators['macd_signal']:.4f}")
        
        if indicators['bb_upper'] and indicators['bb_lower']:
            print(f"✓ Bollinger Bands:")
            print(f"  Upper: ₹{indicators['bb_upper']:.2f}")
            print(f"  Middle: ₹{indicators['bb_middle']:.2f}")
            print(f"  Lower: ₹{indicators['bb_lower']:.2f}")
        
        if indicators['sma20'] and indicators['sma50']:
            print(f"✓ SMA 20: ₹{indicators['sma20']:.2f}")
            print(f"✓ SMA 50: ₹{indicators['sma50']:.2f}")
            if indicators['sma200']:
                print(f"✓ SMA 200: ₹{indicators['sma200']:.2f}")
        
        print(f"\n✓ Technical analysis working!")
        return True
        
    except Exception as e:
        print(f"✗ Technical analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Technical Analysis Test ===")
    test_technical_analysis()