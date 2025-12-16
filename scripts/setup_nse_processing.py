#!/usr/bin/env python3
"""
NSE Stock Analysis Setup Script
Prepares the system for processing all NSE stocks
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.logger import get_logger
from config.settings import settings
from data.nse_data_processor import NSEDataProcessor
from data.batch_scheduler import BatchScheduler, run_test_batch
from core.s3_client import S3Client
from core.dynamodb_client import DynamoDBClient

logger = get_logger(__name__)

class NSESetupManager:
    """Setup and validate NSE processing environment"""
    
    def __init__(self):
        self.processor = NSEDataProcessor()
        self.scheduler = BatchScheduler()
        self.s3_client = S3Client()
        self.db_client = DynamoDBClient()
    
    def validate_environment(self) -> bool:
        """Validate all required components"""
        logger.info("🔍 Validating environment...")
        
        checks = []
        
        # Check CSV file
        csv_exists = Path(self.processor.csv_path).exists()
        checks.append(("NSE Equity CSV", csv_exists))
        
        # Check AWS credentials
        aws_configured = bool(settings.AWS_ACCESS_KEY and settings.AWS_SECRET_KEY)
        checks.append(("AWS Credentials", aws_configured))
        
        # Check S3 bucket
        s3_available = self.s3_client.s3_client is not None
        checks.append(("S3 Client", s3_available))
        
        # Check DynamoDB
        db_available = self.db_client.dynamodb is not None
        checks.append(("DynamoDB Client", db_available))
        
        # Check API keys
        openai_key = bool(settings.OPENAI_API_KEY)
        checks.append(("OpenAI API Key", openai_key))
        
        news_key = bool(settings.NEWS_API_KEY)
        checks.append(("News API Key", news_key))
        
        # Print results
        logger.info("📋 Environment Check Results:")
        all_passed = True
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def analyze_nse_data(self):
        """Analyze the NSE equity data"""
        logger.info("📊 Analyzing NSE equity data...")
        
        try:
            stocks = self.processor.load_nse_stocks()
            
            if not stocks:
                logger.error("❌ No stocks loaded from CSV")
                return
            
            # Group analysis
            groups = {}
            priorities = {}
            
            for stock in stocks:
                group = stock['group']
                priority = stock['priority']
                
                groups[group] = groups.get(group, 0) + 1
                priorities[priority] = priorities.get(priority, 0) + 1
            
            logger.info(f"📈 Total Active Stocks: {len(stocks)}")
            logger.info("📊 By Group:")
            for group, count in sorted(groups.items()):
                logger.info(f"  Group {group}: {count} stocks")
            
            logger.info("🎯 By Priority:")
            for priority, count in priorities.items():
                logger.info(f"  {priority.title()}: {count} stocks")
            
            # Sample stocks
            logger.info("📋 Sample Priority Stocks:")
            priority_stocks = [s for s in stocks if s['priority'] == 'high'][:10]
            for stock in priority_stocks:
                logger.info(f"  {stock['symbol']} - {stock['name']}")
            
        except Exception as e:
            logger.error(f"Error analyzing NSE data: {str(e)}")
    
    async def run_test_processing(self, limit: int = 3):
        """Run test processing on a few stocks"""
        logger.info(f"🧪 Running test processing on {limit} stocks...")
        
        try:
            results = await run_test_batch(limit)
            
            logger.info("🎉 Test Results:")
            logger.info(f"  ✅ Processed: {results['processed_successfully']}")
            logger.info(f"  ❌ Failed: {results['failed']}")
            logger.info(f"  📊 Success Rate: {results['success_rate']}%")
            logger.info(f"  ⏱️ Duration: {results['duration_seconds']}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Test processing failed: {str(e)}")
            return None
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("📁 Creating directories...")
        
        directories = [
            "logs",
            "data/cache",
            "results",
            "backups"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"  📂 {dir_path}")
    
    def show_usage_guide(self):
        """Show usage guide"""
        logger.info("📖 NSE Stock Analysis Usage Guide:")
        logger.info("")
        logger.info("🚀 Quick Start:")
        logger.info("  python scripts/setup_nse_processing.py")
        logger.info("")
        logger.info("🧪 Test Processing (3 stocks):")
        logger.info("  python -m data.batch_scheduler test 3")
        logger.info("")
        logger.info("⚡ Priority Stocks Only:")
        logger.info("  python -m data.batch_scheduler priority")
        logger.info("")
        logger.info("📊 Full NSE Processing:")
        logger.info("  python -m data.batch_scheduler full")
        logger.info("")
        logger.info("📅 Start Scheduled Jobs:")
        logger.info("  python -m data.batch_scheduler schedule")
        logger.info("")
        logger.info("🔧 Configuration:")
        logger.info(f"  Batch Size: {settings.BATCH_SIZE}")
        logger.info(f"  Max Duration: {settings.BATCH_MAX_DURATION_SECONDS}s")
        logger.info(f"  Parallel Workers: {settings.BATCH_PARALLEL_WORKERS}")
        logger.info("")

async def main():
    """Main setup function"""
    logger.info("🚀 NSE Stock Analysis Setup")
    logger.info("=" * 50)
    
    setup = NSESetupManager()
    
    # Create directories
    setup.create_directories()
    
    # Validate environment
    if not setup.validate_environment():
        logger.error("❌ Environment validation failed!")
        logger.info("💡 Please check your configuration in .env file")
        return False
    
    # Analyze NSE data
    setup.analyze_nse_data()
    
    # Run test processing
    logger.info("\n" + "=" * 50)
    test_results = await setup.run_test_processing(limit=3)
    
    if test_results and test_results['processed_successfully'] > 0:
        logger.info("✅ Setup completed successfully!")
        logger.info("\n" + "=" * 50)
        setup.show_usage_guide()
        return True
    else:
        logger.error("❌ Test processing failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)