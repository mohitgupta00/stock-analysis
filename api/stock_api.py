from flask import Flask, jsonify, request
import asyncio
from agents.stock_agent import StockAnalysisAgent

app = Flask(__name__)
agent = StockAnalysisAgent()

@app.route('/analyze/<ticker>')
def analyze_stock(ticker):
    """API endpoint for stock analysis"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.analyze_stock(ticker))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)