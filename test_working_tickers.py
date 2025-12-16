#!/usr/bin/env python3
"""Test with known working NSE tickers"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ticker_formats():
    """Test different ticker formats"""
    
    from data.pricefetcher import PriceFetcher
    
    # Known working NSE tickers
    test_tickers = [
        "INFY.NS",      # Infosys
        "TCS.NS",       # TCS
        "RELIANCE.NS",  # Reliance
        "HDFCBANK.NS",  # HDFC Bank
        "ICICIBANK.NS", # ICICI Bank
    ]
    
    fetcher = PriceFetcher()
    
    print("Testing known working tickers:")
    working_tickers = []
    
    for ticker in test_tickers:
        try:
            data = fetcher.fetch_price_data(ticker)
            if "error" not in data:
                print(f"✅ {ticker}: ₹{data['current_price']:.2f}")
                working_tickers.append(ticker)
            else:
                print(f"❌ {ticker}: {data['error']}")
        except Exception as e:
            print(f"❌ {ticker}: {e}")
    
    print(f"\nWorking tickers: {len(working_tickers)}/{len(test_tickers)}")
    return working_tickers

def find_nse_ticker_mapping():
    """Find correct ticker mapping from NSE data"""
    
    import pandas as pd
    
    # Load clean NSE data
    df = pd.read_csv('/home/sagemaker-user/stock-analysis/data/nse_stocks_clean.csv')
    
    # Look for known companies
    known_companies = ['Infosys', 'TCS', 'Reliance', 'HDFC Bank', 'ICICI Bank']
    
    print("\nSearching for known companies in NSE data:")
    
    for company in known_companies:
        matches = df[df['issuer_name'].str.contains(company, case=False, na=False)]
        if not matches.empty:
            for _, row in matches.iterrows():
                print(f"  {company}: {row['security_code']} -> {row['security_id']} ({row['issuer_name']})")

def create_ticker_test():
    """Create test with correct ticker mapping"""
    
    # Manual mapping of known working tickers
    ticker_map = {
        'INFY.NS': {'code': 'INFY', 'name': 'Infosys Limited'},
        'TCS.NS': {'code': 'TCS', 'name': 'Tata Consultancy Services'},
        'RELIANCE.NS': {'code': 'RELIANCE', 'name': 'Reliance Industries'},
        'HDFCBANK.NS': {'code': 'HDFCBANK', 'name': 'HDFC Bank'},
        'ICICIBANK.NS': {'code': 'ICICIBANK', 'name': 'ICICI Bank'}
    }
    
    from data.pricefetcher import PriceFetcher
    from data.technicalcalculator import TechnicalCalculator
    import yfinance as yf
    
    fetcher = PriceFetcher()
    tech_calc = TechnicalCalculator()
    
    print("\nTesting with correct ticker mapping:")
    results = []
    
    for ticker, info in ticker_map.items():
        print(f"\n--- {ticker} ({info['name']}) ---")
        
        try:
            # Price data
            price_data = fetcher.fetch_price_data(ticker)
            if "error" not in price_data:
                print(f"✅ Price: ₹{price_data['current_price']:.2f}")
                
                # Technical data
                hist = yf.Ticker(ticker).history(period="3mo")
                if not hist.empty:
                    indicators = tech_calc.calculate_indicators(hist)
                    if "error" not in indicators:
                        print(f"✅ RSI: {indicators.get('rsi14', 'N/A')}")
                
                results.append({
                    "ticker": ticker,
                    "status": "success",
                    "price": price_data['current_price']
                })
            else:
                print(f"❌ Failed: {price_data['error']}")
                results.append({"ticker": ticker, "status": "failed"})
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\n=== Test Results ===")
    print(f"Successful: {successful}/{len(ticker_map)}")
    
    if successful >= 3:
        print("\n🎉 System ready for processing!")
        print("\nRecommendation:")
        print("  • Use Security ID (not Security Code) for ticker mapping")
        print("  • Focus on liquid stocks with active trading")
        print("  • Start with Group A stocks for better success rate")
    
    return successful >= 3

if __name__ == "__main__":
    print("=== NSE Ticker Format Test ===")
    
    working_tickers = test_ticker_formats()
    find_nse_ticker_mapping()
    success = create_ticker_test()
    
    if success:
        print("\n✅ Ready to proceed with full system testing")