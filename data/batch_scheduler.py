import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
from config.logger import get_logger
from config.settings import settings
from data.nse_data_processor import NSEDataProcessor
from core.s3_client import S3Client
from core.dynamodb_client import DynamoDBClient

logger = get_logger(__name__)

class BatchScheduler:
    """Schedule and manage batch processing of NSE stocks"""
    
    def __init__(self):
        self.processor = NSEDataProcessor()
        self.s3_client = S3Client()
        self.db_client = DynamoDBClient()
        self.is_running = False
        
    async def daily_full_refresh(self):
        """Run daily full refresh of all NSE stocks"""
        if self.is_running:
            logger.warning("⚠️ Batch job already running, skipping...")
            return
        
        self.is_running = True
        logger.info("🌅 Starting daily full refresh...")
        
        try:
            # Process all stocks
            results = await self.processor.process_all_nse_stocks()
            
            # Store results in S3
            date_str = datetime.now().strftime("%Y%m%d")
            s3_key = f"daily-analysis/{date_str}/nse_full_analysis.json"
            
            success = self.s3_client.upload_json(s3_key, results)
            
            if success:
                logger.info(f"📤 Results uploaded to S3: {s3_key}")
                
                # Store summary in DynamoDB
                await self.store_batch_summary(results, date_str)
            
            # Store checkpoint
            self.db_client.store_checkpoint(
                results['processed_successfully'],
                results['total_stocks']
            )
            
            logger.info("✅ Daily refresh completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Daily refresh failed: {str(e)}")
            
            # Store failed tickers for retry
            failed_tickers = self.extract_failed_tickers(results)
            if failed_tickers:
                self.db_client.store_failed_tickers(failed_tickers)
        
        finally:
            self.is_running = False
    
    async def priority_stocks_refresh(self):
        """Quick refresh of priority stocks (Group A)"""
        logger.info("⚡ Starting priority stocks refresh...")
        
        try:
            # Load only Group A stocks
            stocks = self.processor.load_nse_stocks()
            priority_stocks = [s for s in stocks if s['priority'] == 'high']
            
            logger.info(f"🎯 Processing {len(priority_stocks)} priority stocks")
            
            # Process priority stocks
            results = await self.processor.process_stock_batch(priority_stocks, batch_size=20)
            
            # Store in S3
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            s3_key = f"priority-analysis/{timestamp}/priority_stocks.json"
            
            summary = {
                'type': 'priority_refresh',
                'timestamp': datetime.now().isoformat(),
                'processed_count': len(results),
                'results': results
            }
            
            self.s3_client.upload_json(s3_key, summary)
            logger.info("✅ Priority refresh completed")
            
        except Exception as e:
            logger.error(f"❌ Priority refresh failed: {str(e)}")
    
    async def retry_failed_stocks(self):
        """Retry processing failed stocks from previous runs"""
        logger.info("🔄 Starting retry of failed stocks...")
        
        try:
            # Get failed tickers from DynamoDB
            today = datetime.now().strftime("%Y%m%d")
            failed_data = self.db_client.get_item(
                'batch_failed_tickers',
                {'batch_date': today}
            )
            
            if not failed_data or not failed_data.get('failed_tickers'):
                logger.info("📝 No failed stocks to retry")
                return
            
            failed_tickers = failed_data['failed_tickers']
            logger.info(f"🔄 Retrying {len(failed_tickers)} failed stocks")
            
            # Convert tickers to stock objects
            all_stocks = self.processor.load_nse_stocks()
            retry_stocks = [s for s in all_stocks if s['symbol'] in failed_tickers]
            
            # Process retry stocks
            results = await self.processor.process_stock_batch(retry_stocks, batch_size=5)
            
            # Update failed list
            still_failed = []
            for stock in retry_stocks:
                if not any(r.get('ticker') == stock['symbol'] for r in results):
                    still_failed.append(stock['symbol'])
            
            if still_failed:
                self.db_client.store_failed_tickers(still_failed)
                logger.warning(f"⚠️ {len(still_failed)} stocks still failing")
            else:
                logger.info("✅ All retry attempts successful")
            
        except Exception as e:
            logger.error(f"❌ Retry failed: {str(e)}")
    
    async def store_batch_summary(self, results: Dict, date_str: str):
        """Store batch processing summary in DynamoDB"""
        try:
            summary_item = {
                'batch_date': date_str,
                'total_stocks': results['total_stocks'],
                'processed_successfully': results['processed_successfully'],
                'failed_count': results['failed'],
                'success_rate': results['success_rate'],
                'duration_seconds': results['duration_seconds'],
                'stocks_per_minute': results['stocks_per_minute'],
                'timestamp': results['timestamp']
            }
            
            success = self.db_client.put_item('batch_summary', summary_item)
            
            if success:
                logger.info("📊 Batch summary stored in DynamoDB")
            
        except Exception as e:
            logger.error(f"Error storing batch summary: {str(e)}")
    
    def extract_failed_tickers(self, results: Dict) -> List[str]:
        """Extract failed ticker symbols from results"""
        try:
            failed_tickers = []
            # This would need to be implemented based on your results structure
            # For now, return empty list
            return failed_tickers
        except Exception:
            return []
    
    def setup_schedule(self):
        """Setup the scheduling for batch jobs"""
        logger.info("📅 Setting up batch job schedule...")
        
        # Daily full refresh at 6 AM IST
        schedule.every().day.at("06:00").do(
            lambda: asyncio.create_task(self.daily_full_refresh())
        )
        
        # Priority stocks refresh every 4 hours during market hours
        schedule.every().day.at("09:30").do(
            lambda: asyncio.create_task(self.priority_stocks_refresh())
        )
        schedule.every().day.at("13:30").do(
            lambda: asyncio.create_task(self.priority_stocks_refresh())
        )
        
        # Retry failed stocks at 8 PM
        schedule.every().day.at("20:00").do(
            lambda: asyncio.create_task(self.retry_failed_stocks())
        )
        
        logger.info("✅ Schedule configured:")
        logger.info("  📊 Daily full refresh: 6:00 AM IST")
        logger.info("  ⚡ Priority refresh: 9:30 AM, 1:30 PM IST")
        logger.info("  🔄 Retry failed: 8:00 PM IST")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info("🚀 Starting batch scheduler...")
        
        self.setup_schedule()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error

# Manual execution functions
async def run_full_batch():
    """Manually run full batch processing"""
    scheduler = BatchScheduler()
    await scheduler.daily_full_refresh()

async def run_priority_batch():
    """Manually run priority stocks batch"""
    scheduler = BatchScheduler()
    await scheduler.priority_stocks_refresh()

async def run_test_batch(limit: int = 10):
    """Run test batch with limited stocks"""
    processor = NSEDataProcessor()
    results = await processor.process_all_nse_stocks(limit=limit)
    processor.save_results(results, f"test_batch_{limit}_stocks.json")
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "schedule":
            # Run continuous scheduler
            scheduler = BatchScheduler()
            scheduler.run_scheduler()
            
        elif command == "full":
            # Run full batch once
            asyncio.run(run_full_batch())
            
        elif command == "priority":
            # Run priority batch once
            asyncio.run(run_priority_batch())
            
        elif command == "test":
            # Run test batch
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            asyncio.run(run_test_batch(limit))
            
        else:
            print("Usage: python batch_scheduler.py [schedule|full|priority|test] [limit]")
    else:
        print("Usage: python batch_scheduler.py [schedule|full|priority|test] [limit]")