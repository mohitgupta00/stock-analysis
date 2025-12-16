import pandas as pd
import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from config.logger import get_logger
from config.settings import settings
from data.datafetcherunified import ComprehensiveDataFetcher

logger = get_logger(__name__)

class NSEDataProcessor:
    """Process all NSE stocks from Equity.csv"""
    
    def __init__(self, csv_path: str = "/home/sagemaker-user/shared/Equity.csv"):
        self.csv_path = csv_path
        self.data_fetcher = ComprehensiveDataFetcher()
        self.processed_count = 0
        self.failed_count = 0
        self.results = []
        
    def load_nse_stocks(self) -> List[Dict]:
        """Load NSE stocks from clean CSV"""
        try:
            # Use clean CSV file
            import os
            clean_file = os.path.join(os.path.dirname(__file__), 'nse_stocks_clean.csv')
            
            if not os.path.exists(clean_file):
                logger.error(f"Clean NSE file not found: {clean_file}")
                return []
            
            df = pd.read_csv(clean_file)
            logger.info(f"📊 Loaded {len(df)} active NSE stocks")
            
            # Prioritize by group (A = Large Cap)
            priority_stocks = df[df['group'] == 'A'].copy()
            other_stocks = df[df['group'] != 'A'].copy()
            
            logger.info(f"🎯 Priority stocks (Group A): {len(priority_stocks)}")
            logger.info(f"📈 Other stocks: {len(other_stocks)}")
            
            stocks_list = []
            
            # Add priority stocks first
            for _, row in priority_stocks.iterrows():
                stocks_list.append({
                    'ticker': f"{row['security_id']}.NS",
                    'name': row['issuer_name'],
                    'symbol': row['security_id'],
                    'code': row['security_code'],
                    'group': row['group'],
                    'face_value': row['face_value'],
                    'isin': row['isin'],
                    'priority': 'high'
                })
            
            # Add other stocks
            for _, row in other_stocks.iterrows():
                stocks_list.append({
                    'ticker': f"{row['security_id']}.NS",
                    'name': row['issuer_name'],
                    'symbol': row['security_id'],
                    'code': row['security_code'],
                    'group': row['group'],
                    'face_value': row['face_value'],
                    'isin': row['isin'],
                    'priority': 'normal'
                })
            
            return stocks_list
            
        except Exception as e:
            logger.error(f"Error loading NSE stocks: {str(e)}")
            return []
    
    async def process_stock_batch(self, stocks: List[Dict], batch_size: int = 10) -> List[Dict]:
        """Process stocks in batches with rate limiting"""
        results = []
        
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i + batch_size]
            batch_start = time.time()
            
            logger.info(f"🔄 Processing batch {i//batch_size + 1}: stocks {i+1}-{min(i+batch_size, len(stocks))}")
            
            # Process batch in parallel
            tasks = []
            for stock in batch:
                task = self.process_single_stock(stock)
                tasks.append(task)
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Failed {batch[j]['symbol']}: {str(result)}")
                        self.failed_count += 1
                    else:
                        logger.info(f"✅ Processed {batch[j]['symbol']}")
                        self.processed_count += 1
                        results.append(result)
                
                # Rate limiting between batches
                batch_duration = time.time() - batch_start
                if batch_duration < 2.0:  # Minimum 2 seconds between batches
                    await asyncio.sleep(2.0 - batch_duration)
                
            except Exception as e:
                logger.error(f"Batch processing error: {str(e)}")
                self.failed_count += len(batch)
        
        return results
    
    async def process_single_stock(self, stock: Dict) -> Dict:
        """Process a single stock"""
        ticker = stock['symbol']
        
        try:
            # Fetch comprehensive data
            data = await self.data_fetcher.fetch_complete_analysis_data_async(ticker)
            
            # Add NSE metadata
            data['nse_metadata'] = stock
            data['processing_timestamp'] = datetime.now().isoformat()
            
            return data
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            raise
    
    async def process_all_nse_stocks(self, limit: Optional[int] = None) -> Dict:
        """Process all NSE stocks with progress tracking"""
        logger.info("🚀 Starting NSE stock processing...")
        
        # Load stocks
        stocks = self.load_nse_stocks()
        
        if limit:
            stocks = stocks[:limit]
            logger.info(f"🎯 Processing limited set: {limit} stocks")
        
        total_stocks = len(stocks)
        logger.info(f"📊 Total stocks to process: {total_stocks}")
        
        start_time = time.time()
        
        # Process in batches
        results = await self.process_stock_batch(stocks, batch_size=settings.BATCH_SIZE)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Summary
        summary = {
            'total_stocks': total_stocks,
            'processed_successfully': self.processed_count,
            'failed': self.failed_count,
            'success_rate': round(self.processed_count / total_stocks * 100, 2) if total_stocks > 0 else 0,
            'duration_seconds': round(duration, 2),
            'stocks_per_minute': round(self.processed_count / (duration / 60), 2) if duration > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        logger.info(f"🎉 Processing complete!")
        logger.info(f"✅ Success: {self.processed_count}/{total_stocks} ({summary['success_rate']}%)")
        logger.info(f"⏱️ Duration: {duration:.1f}s ({summary['stocks_per_minute']:.1f} stocks/min)")
        
        return summary
    
    def save_results(self, results: Dict, output_path: str = "nse_analysis_results.json"):
        """Save results to file"""
        try:
            import json
            
            output_file = Path(output_path)
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"💾 Results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

# Test function
async def test_nse_processor():
    """Test the NSE processor with a small sample"""
    processor = NSEDataProcessor()
    
    # Test with first 5 stocks
    results = await processor.process_all_nse_stocks(limit=5)
    
    # Save results
    processor.save_results(results, "test_nse_results.json")
    
    return results

if __name__ == "__main__":
    # Run test
    asyncio.run(test_nse_processor())