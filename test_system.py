#!/usr/bin/env python3
"""
Quick system test for NSE stock analysis
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.logger import get_logger
from data.nse_data_processor import NSEDataProcessor

logger = get_logger(__name__)

async def test_nse_system():
    """Test the NSE processing system"""
    
    print("🧪 Testing NSE Stock Analysis System")
    print("=" * 40)
    
    try:
        # Initialize processor
        processor = NSEDataProcessor()
        
        # Test 1: Load NSE data
        print("📊 Test 1: Loading NSE equity data...")
        stocks = processor.load_nse_stocks()
        
        if stocks:
            print(f"✅ Loaded {len(stocks)} stocks")
            print(f"📈 Priority stocks: {len([s for s in stocks if s['priority'] == 'high'])}")
            
            # Show sample
            print("\n📋 Sample stocks:")
            for i, stock in enumerate(stocks[:5]):
                print(f"  {i+1}. {stock['symbol']} - {stock['name']}")
        else:
            print("❌ Failed to load stocks")
            return False
        
        # Test 2: Process one stock
        print(f"\n🔍 Test 2: Processing sample stock...")
        test_stock = stocks[0]  # First stock
        
        try:
            result = await processor.process_single_stock(test_stock)
            
            if result and not result.get('errors'):
                print(f"✅ Successfully processed {test_stock['symbol']}")
                print(f"📊 Data sections: {list(result.keys())}")
            else:
                print(f"⚠️ Processed with errors: {result.get('errors', [])}")
            
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
            return False
        
        print("\n🎉 System test completed successfully!")
        print("\n📖 Next steps:")
        print("  python run_nse_analysis.py test 5      # Test with 5 stocks")
        print("  python run_nse_analysis.py priority    # Process priority stocks")
        print("  python run_nse_analysis.py full        # Process all stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_nse_system())
    sys.exit(0 if success else 1)