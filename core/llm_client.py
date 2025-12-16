import boto3
import json
from config.settings import AWS_REGION, BEDROCK_MODEL_ID, LLM_MAX_TOKENS, LLM_TEMPERATURE

class BedrockLLMClient:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        self.model_id = BEDROCK_MODEL_ID
    
    def analyze_stock_data(self, stock_data):
        """Generate stock analysis using AWS Bedrock"""
        prompt = self._create_analysis_prompt(stock_data)
        
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": LLM_MAX_TOKENS,
                    "temperature": LLM_TEMPERATURE,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def _create_analysis_prompt(self, data):
        ticker = data.get('ticker', 'Unknown')
        price = data.get('price', {})
        fundamentals = data.get('fundamentals', {})
        technical = data.get('technical', {})
        
        return f"""Analyze this stock data for {ticker}:

PRICE DATA:
- Current: ${price.get('current_price', 'N/A')}
- 52W High: ${price.get('high_52w', 'N/A')}
- 52W Low: ${price.get('low_52w', 'N/A')}

FUNDAMENTALS:
- Company: {fundamentals.get('company_name', 'N/A')}
- Sector: {fundamentals.get('sector', 'N/A')}
- P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
- Market Cap: {fundamentals.get('market_cap', 'N/A')}

TECHNICAL:
- RSI: {technical.get('rsi14', 'N/A')}
- SMA20: ${technical.get('sma20', 'N/A')}
- SMA50: ${technical.get('sma50', 'N/A')}

Provide a concise investment analysis with key insights and risk factors."""