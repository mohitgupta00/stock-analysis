#!/usr/bin/env python3
"""
NSE Stock Analysis - Main Runner
Quick execution script for NSE stock processing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.logger import get_logger
from data.nse_data_processor import NSEDataProcessor
from data.batch_scheduler import BatchScheduler

logger = get_logger(__name__)

async def main():
    """Main execution function"""
    
    print("🚀 NSE Stock Analysis System")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_nse_analysis.py test [limit]     # Test with limited stocks")
        print("  python run_nse_analysis.py priority         # Process priority stocks only")
        print("  python run_nse_analysis.py full             # Process all NSE stocks")
        print("  python run_nse_analysis.py schedule         # Start scheduled processing")
        print("")
        print("Examples:")
        print("  python run_nse_analysis.py test 5           # Test with 5 stocks")
        print("  python run_nse_analysis.py priority         # Priority stocks")
        print("  python run_nse_analysis.py full             # All ~4000 stocks")
        return
    
    command = sys.argv[1].lower()
    
    if command == "test":
        # Test processing
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        logger.info(f"🧪 Testing with {limit} stocks...")
        
        processor = NSEDataProcessor()
        results = await processor.process_all_nse_stocks(limit=limit)
        
        # Save results
        output_file = f"test_results_{limit}_stocks_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        processor.save_results(results, output_file)
        
        print(f"\n✅ Test completed!")
        print(f"📊 Processed: {results['processed_successfully']}/{results['total_stocks']}")
        print(f"📁 Results saved: {output_file}")
    
    elif command == "priority":
        # Priority stocks only
        logger.info("⚡ Processing priority stocks...")
        
        scheduler = BatchScheduler()
        await scheduler.priority_stocks_refresh()
        
        print("✅ Priority stocks processing completed!")
    
    elif command == "full":
        # Full NSE processing
        logger.info("📊 Processing ALL NSE stocks...")
        
        processor = NSEDataProcessor()
        results = await processor.process_all_nse_stocks()
        
        # Save results
        output_file = f"nse_full_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        processor.save_results(results, output_file)
        
        print(f"\n🎉 Full processing completed!")
        print(f"📊 Processed: {results['processed_successfully']}/{results['total_stocks']}")
        print(f"⏱️ Duration: {results['duration_seconds']:.1f}s")
        print(f"📁 Results saved: {output_file}")
    
    elif command == "schedule":
        # Start scheduled processing
        logger.info("📅 Starting scheduled processing...")
        
        scheduler = BatchScheduler()
        scheduler.run_scheduler()  # This runs indefinitely
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use: test, priority, full, or schedule")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)