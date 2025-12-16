#!/usr/bin/env python3
"""Test NSE processor with clean data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nse_loading():
    """Test NSE stock loading"""
    
    from data.nse_data_processor import NSEDataProcessor
    
    processor = NSEDataProcessor()
    
    # Test loading stocks
    stocks = processor.load_nse_stocks()
    
    if stocks:
        print(f"✅ Loaded {len(stocks)} NSE stocks")
        
        # Show priority stocks
        priority_stocks = [s for s in stocks if s['priority'] == 'high']
        print(f"🎯 Priority stocks (Group A): {len(priority_stocks)}")
        
        # Show sample
        print("\nSample stocks:")
        for i, stock in enumerate(stocks[:5]):
            print(f"  {i+1}. {stock['ticker']} - {stock['name']} (Group {stock['group']})")
        
        return True
    else:
        print("❌ Failed to load NSE stocks")
        return False

def test_simple_processing():
    """Test processing with simple data fetcher"""
    
    from data.pricefetcher import PriceFetcher
    from data.technicalcalculator import TechnicalCalculator
    import yfinance as yf
    
    # Test with first 3 stocks from clean data
    import pandas as pd
    clean_file = '/home/sagemaker-user/stock-analysis/data/nse_stocks_clean.csv'
    df = pd.read_csv(clean_file)
    
    test_stocks = df.head(3)
    
    fetcher = PriceFetcher()
    tech_calc = TechnicalCalculator()
    
    results = []
    
    for _, stock in test_stocks.iterrows():
        ticker = f"{stock['security_code']}.NS"
        print(f"\n--- Testing {ticker} ({stock['issuer_name']}) ---")
        
        try:
            # Get price data
            price_data = fetcher.fetch_price_data(ticker)
            if "error" not in price_data:
                print(f"✅ Price: ₹{price_data['current_price']:.2f}")
                
                # Get technical data
                hist = yf.Ticker(ticker).history(period="3mo")
                if not hist.empty:
                    indicators = tech_calc.calculate_indicators(hist)
                    if "error" not in indicators:
                        print(f"✅ RSI: {indicators.get('rsi14', 'N/A')}")
                        print(f"✅ SMA20: ₹{indicators.get('sma20', 0):.2f}")
                
                results.append({
                    "ticker": ticker,
                    "status": "success",
                    "price": price_data['current_price']
                })
            else:
                print(f"❌ Price fetch failed: {price_data['error']}")
                results.append({"ticker": ticker, "status": "failed"})
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"ticker": ticker, "status": "error"})
    
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n=== Results ===")
    print(f"Successful: {successful}/{len(results)}")
    
    return successful > 0

if __name__ == "__main__":
    print("=== NSE Processor Test ===")
    
    print("\n1. Testing NSE data loading...")
    loading_ok = test_nse_loading()
    
    print("\n2. Testing simple processing...")
    processing_ok = test_simple_processing()
    
    if loading_ok and processing_ok:
        print("\n🎉 NSE processor is ready!")
        print("\nNext steps:")
        print("  python run_nse_analysis.py test 5")
        print("  python run_nse_analysis.py priority")
    else:
        print("\n❌ Some tests failed")