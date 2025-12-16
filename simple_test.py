#!/usr/bin/env python3
"""Simple test of core functionality"""

import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nse_data_and_price():
    """Test NSE data loading and price fetching"""
    try:
        # Test NSE data
        nse_file = "/home/sagemaker-user/shared/Equity.csv"
        df = pd.read_csv(nse_file)
        
        # Get first 3 active stocks (handle spaces in column names)
        df.columns = df.columns.str.strip()
        active_stocks = df[df['Status'] == 'Active'].head(3)
        print(f"Testing with {len(active_stocks)} stocks:")
        
        from data.pricefetcher import PriceFetcher
        from data.technicalcalculator import TechnicalCalculator
        
        fetcher = PriceFetcher()
        tech_calc = TechnicalCalculator()
        
        results = []
        
        for _, stock in active_stocks.iterrows():
            ticker = f"{stock['Security Code']}.NS"
            print(f"\n--- Testing {stock['Security Code']} ({stock['Issuer Name']}) ---")
            
            # Test price data
            price_data = fetcher.fetch_price_data(ticker)
            if "error" not in price_data:
                print(f"✓ Price: ₹{price_data['current_price']:.2f}")
                
                # Test fundamentals
                fundamentals = fetcher.fetch_fundamentals(ticker)
                if "error" not in fundamentals:
                    print(f"✓ Sector: {fundamentals.get('sector', 'N/A')}")
                    print(f"✓ Market Cap: ₹{fundamentals.get('market_cap', 0):,}")
                else:
                    print(f"⚠ Fundamentals: {fundamentals['error']}")
                
                results.append({
                    "ticker": ticker,
                    "price": price_data['current_price'],
                    "status": "success"
                })
            else:
                print(f"✗ Price fetch failed: {price_data['error']}")
                results.append({
                    "ticker": ticker,
                    "status": "failed",
                    "error": price_data['error']
                })
        
        print(f"\n=== Summary ===")
        successful = len([r for r in results if r['status'] == 'success'])
        print(f"Successful: {successful}/{len(results)}")
        
        if successful > 0:
            print("✓ System is working! You can now:")
            print("  1. Test more stocks manually")
            print("  2. Set up AWS credentials for full analysis")
            print("  3. Run batch processing when ready")
        
        return successful > 0
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Simple Stock Analysis Test ===")
    test_nse_data_and_price()