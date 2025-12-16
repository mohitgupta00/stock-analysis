#!/usr/bin/env python3
"""Fix NSE CSV parsing and create clean stock list"""

import pandas as pd
import re

def fix_nse_csv():
    """Parse and clean NSE equity data"""
    
    # Read raw CSV with proper parsing
    with open('/home/sagemaker-user/shared/Equity.csv', 'r') as f:
        lines = f.readlines()
    
    # Parse manually to handle formatting issues
    stocks = []
    header_processed = False
    
    for line in lines[1:]:  # Skip header
        parts = line.strip().split(',')
        if len(parts) >= 9:
            try:
                stock = {
                    'security_code': parts[0].strip(),
                    'issuer_name': parts[1].strip(),
                    'security_id': parts[2].strip(),
                    'security_name': parts[3].strip(),
                    'status': parts[4].strip(),
                    'group': parts[5].strip(),
                    'face_value': parts[6].strip(),
                    'isin': parts[7].strip(),
                    'instrument': parts[8].strip()
                }
                
                # Filter active stocks only
                if stock['status'] == 'Active' and stock['security_code']:
                    stocks.append(stock)
                    
            except Exception as e:
                continue
    
    print(f"Parsed {len(stocks)} active NSE stocks")
    
    # Create clean DataFrame
    df = pd.DataFrame(stocks)
    
    # Save cleaned data
    clean_file = '/home/sagemaker-user/stock-analysis/data/nse_stocks_clean.csv'
    df.to_csv(clean_file, index=False)
    print(f"Saved clean data to: {clean_file}")
    
    # Show sample
    print("\nSample stocks:")
    print(df.head()[['security_code', 'issuer_name', 'group']])
    
    # Group statistics
    print(f"\nGroup distribution:")
    print(df['group'].value_counts().head())
    
    return df

if __name__ == "__main__":
    fix_nse_csv()