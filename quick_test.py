#!/usr/bin/env python3
"""Quick system test without external dependencies"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test data modules
        from data.pricefetcher import PriceFetcher
        print("✓ PriceFetcher imported")
        
        from data.technicalcalculator import TechnicalCalculator
        print("✓ TechnicalCalculator imported")
        
        # Test if NSE data file exists
        nse_file = "/home/sagemaker-user/shared/Equity.csv"
        if os.path.exists(nse_file):
            print(f"✓ NSE data file found: {nse_file}")
        else:
            print(f"✗ NSE data file missing: {nse_file}")
            
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_nse_data():
    """Test NSE data loading"""
    try:
        import pandas as pd
        nse_file = "/home/sagemaker-user/shared/Equity.csv"
        
        if not os.path.exists(nse_file):
            print(f"✗ NSE file not found: {nse_file}")
            return False
            
        df = pd.read_csv(nse_file)
        print(f"✓ Loaded NSE data: {len(df)} stocks")
        
        if len(df) > 0:
            print(f"  Sample: {df.iloc[0]['Security Code']} - {df.iloc[0]['Issuer Name']}")
        
        return True
    except Exception as e:
        print(f"✗ NSE data test failed: {e}")
        return False

def test_price_fetcher():
    """Test price fetching with a sample stock"""
    try:
        from data.pricefetcher import PriceFetcher
        fetcher = PriceFetcher()
        
        # Test with INFY (Infosys)
        data = fetcher.fetch_price_data("INFY.NS")
        if data and "error" not in data:
            print(f"✓ Price data fetched for INFY: ₹{data['current_price']:.2f}")
            return True
        else:
            print(f"✗ Price fetch failed: {data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Price fetcher test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Quick System Test ===\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("NSE Data Loading", test_nse_data),
        ("Price Fetching", test_price_fetcher)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        if test_func():
            passed += 1
        
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Run: python run_nse_analysis.py test 3")
        print("2. Run: python run_nse_analysis.py priority")
    else:
        print("✗ Some tests failed. Check the errors above.")