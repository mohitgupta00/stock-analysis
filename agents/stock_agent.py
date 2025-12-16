import asyncio
from data.datafetcherunified import ComprehensiveDataFetcher
from core.llm_client import BedrockLLMClient

class StockAnalysisAgent:
    def __init__(self):
        self.data_fetcher = ComprehensiveDataFetcher()
        self.llm_client = BedrockLLMClient()
    
    async def analyze_stock(self, ticker):
        """Complete stock analysis pipeline"""
        print(f"🔍 Analyzing {ticker.upper()}...")
        
        # Fetch comprehensive data
        stock_data = await self.data_fetcher.fetch_all_data(ticker)
        
        if stock_data.get('errors'):
            print(f"⚠️ Data fetch warnings: {stock_data['errors']}")
        
        # Generate AI analysis
        print("🤖 Generating AI analysis...")
        analysis = self.llm_client.analyze_stock_data(stock_data)
        
        return {
            "ticker": ticker.upper(),
            "data": stock_data,
            "ai_analysis": analysis,
            "timestamp": stock_data.get('timestamp')
        }
    
    def format_analysis_report(self, analysis_result):
        """Format analysis for display"""
        ticker = analysis_result['ticker']
        data = analysis_result['data']
        ai_analysis = analysis_result['ai_analysis']
        
        report = f"""
📊 STOCK ANALYSIS REPORT: {ticker}
{'='*50}

💰 CURRENT METRICS:
"""
        
        if 'price' in data:
            price = data['price']
            report += f"Current Price: ${price.get('current_price', 'N/A'):.2f}\n"
            report += f"52W Range: ${price.get('low_52w', 'N/A'):.2f} - ${price.get('high_52w', 'N/A'):.2f}\n"
        
        if 'technical' in data:
            tech = data['technical']
            report += f"\n📈 TECHNICAL INDICATORS:\n"
            report += f"RSI(14): {tech.get('rsi14', 'N/A')}\n"
            report += f"SMA20: ${tech.get('sma20', 'N/A'):.2f}\n"
            report += f"SMA50: ${tech.get('sma50', 'N/A'):.2f}\n"
        
        report += f"\n🤖 AI ANALYSIS:\n{ai_analysis}\n"
        report += f"\n⏰ Generated: {analysis_result['timestamp']}"
        
        return report