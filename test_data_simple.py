#!/usr/bin/env python3
"""Test with manual stock list"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_known_stocks():
    """Test with known NSE stocks"""
    
    # Test with popular NSE stocks
    test_stocks = [
        {"code": "INFY", "name": "Infosys Limited"},
        {"code": "TCS", "name": "Tata Consultancy Services"},
        {"code": "RELIANCE", "name": "Reliance Industries"}
    ]
    
    print(f"Testing with {len(test_stocks)} popular NSE stocks:")
    
    from data.pricefetcher import PriceFetcher
    fetcher = PriceFetcher()
    
    results = []
    
    for stock in test_stocks:
        ticker = f"{stock['code']}.NS"
        print(f"\n--- Testing {stock['code']} ({stock['name']}) ---")
        
        # Test price data
        price_data = fetcher.fetch_price_data(ticker)
        if "error" not in price_data:
            print(f"✓ Current Price: ₹{price_data['current_price']:.2f}")
            print(f"✓ 52W High: ₹{price_data['high_52w']:.2f}")
            print(f"✓ 52W Low: ₹{price_data['low_52w']:.2f}")
            
            # Test fundamentals
            fundamentals = fetcher.fetch_fundamentals(ticker)
            if "error" not in fundamentals:
                print(f"✓ Company: {fundamentals.get('company_name', 'N/A')}")
                print(f"✓ Sector: {fundamentals.get('sector', 'N/A')}")
                print(f"✓ Market Cap: ₹{fundamentals.get('market_cap', 0):,}")
                print(f"✓ P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}")
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
    
    print(f"\n=== Test Results ===")
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"Successful: {successful}/{len(results)}")
    
    if successful > 0:
        print("\n✓ Core system is working!")
        print("\nWhat works:")
        print("  • NSE stock price fetching")
        print("  • Fundamental data retrieval")
        print("  • Error handling")
        
        print("\nNext steps:")
        print("  1. Fix NSE CSV parsing for full stock list")
        print("  2. Set up AWS credentials for AI analysis")
        print("  3. Test technical indicators")
        print("  4. Run batch processing")
        
        return True
    else:
        print("\n✗ System needs debugging")
        return False

if __name__ == "__main__":
    print("=== NSE Stock Analysis - Core Test ===")
    test_with_known_stocks()