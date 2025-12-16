import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent
from data.technicalcalculator import TechnicalCalculator
from data.pricefetcher import PriceFetcher
from typing import Dict, Any
import yfinance as yf
from datetime import datetime

class TechnicalAnalysisAgent(BaseAgent):
    """Agent for technical analysis - trends, momentum, volatility"""
    
    def __init__(self):
        super().__init__("Technical_Analysis_Agent", weight=0.25)
        self.tech_calc = TechnicalCalculator()
        self.fetcher = PriceFetcher()
        
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform technical analysis"""
        try:
            # Get historical price data
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")  # 1 year of data
            
            if hist.empty or len(hist) < 50:
                return self._create_error_response("Insufficient historical data")
            
            # Calculate technical indicators
            indicators = self.tech_calc.calculate_indicators(hist)
            
            if "error" in indicators:
                return self._create_error_response(indicators["error"])
            
            # Get current price data
            price_data = self.fetcher.fetch_price_data(ticker)
            
            # Calculate scores
            scores = self._calculate_technical_scores(indicators, price_data, hist)
            
            # Generate analysis
            analysis = self._generate_analysis(indicators, scores, hist)
            
            return self.create_response(
                scores=scores,
                analysis=analysis,
                key_metrics=self._extract_key_metrics(indicators, price_data),
                confidence=self._calculate_confidence(indicators)
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _calculate_technical_scores(self, indicators: Dict[str, Any], 
                                   price_data: Dict[str, Any], hist) -> Dict[str, float]:
        """Calculate technical analysis scores"""
        scores = {}
        
        # Momentum Score (RSI)
        rsi = indicators.get('rsi14')
        momentum_score = 0.5
        
        if rsi:
            if 40 <= rsi <= 60:  # Neutral zone
                momentum_score = 0.6
            elif 30 <= rsi < 40:  # Oversold - potential buy
                momentum_score = 0.8
            elif 60 < rsi <= 70:  # Mild overbought
                momentum_score = 0.4
            elif rsi < 30:  # Deeply oversold
                momentum_score = 0.9
            elif rsi > 80:  # Severely overbought
                momentum_score = 0.2
        
        scores['momentum_score'] = momentum_score
        
        # Trend Score (Moving Averages)
        current_price = indicators.get('current_price', 0)
        sma20 = indicators.get('sma20', 0)
        sma50 = indicators.get('sma50', 0)
        sma200 = indicators.get('sma200', 0)
        
        trend_score = 0.5
        
        if current_price and sma20 and sma50:
            if current_price > sma20 > sma50:  # Strong uptrend
                trend_score = 0.8
                if sma200 and sma50 > sma200:  # Very strong uptrend
                    trend_score = 0.9
            elif current_price < sma20 < sma50:  # Strong downtrend
                trend_score = 0.2
                if sma200 and sma50 < sma200:  # Very strong downtrend
                    trend_score = 0.1
            elif current_price > sma20:  # Mild uptrend
                trend_score = 0.6
            elif current_price < sma20:  # Mild downtrend
                trend_score = 0.4
        
        scores['trend_score'] = trend_score
        
        # MACD Score
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        
        macd_score = 0.5
        if macd is not None and macd_signal is not None:
            if macd > macd_signal and macd > 0:  # Bullish and positive
                macd_score = 0.8
            elif macd > macd_signal and macd < 0:  # Bullish but negative
                macd_score = 0.6
            elif macd < macd_signal and macd < 0:  # Bearish and negative
                macd_score = 0.2
            elif macd < macd_signal and macd > 0:  # Bearish but positive
                macd_score = 0.4
        
        scores['macd_score'] = macd_score
        
        # Volatility Score (Bollinger Bands)
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        
        volatility_score = 0.5
        if current_price and bb_upper and bb_lower:
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            
            if 0.3 <= bb_position <= 0.7:  # Middle of bands - stable
                volatility_score = 0.7
            elif bb_position < 0.2:  # Near lower band - oversold
                volatility_score = 0.8
            elif bb_position > 0.8:  # Near upper band - overbought
                volatility_score = 0.3
        
        scores['volatility_score'] = volatility_score
        
        # Price Position Score (52-week range)
        if "error" not in price_data:
            high_52w = price_data.get('high_52w', 0)
            low_52w = price_data.get('low_52w', 0)
            
            price_position_score = 0.5
            if high_52w and low_52w and current_price:
                position = (current_price - low_52w) / (high_52w - low_52w)
                
                if 0.6 <= position <= 0.8:  # Strong but not at peak
                    price_position_score = 0.8
                elif 0.4 <= position < 0.6:  # Middle range
                    price_position_score = 0.6
                elif position < 0.3:  # Near 52-week low
                    price_position_score = 0.7  # Potential value
                elif position > 0.9:  # Near 52-week high
                    price_position_score = 0.4  # Risky
            
            scores['price_position_score'] = price_position_score
        
        return scores
    
    def _generate_analysis(self, indicators: Dict[str, Any], scores: Dict[str, float], hist) -> str:
        """Generate technical analysis text"""
        
        rsi = indicators.get('rsi14')
        current_price = indicators.get('current_price')
        sma20 = indicators.get('sma20')
        sma50 = indicators.get('sma50')
        
        analysis_parts = []
        
        # RSI analysis
        if rsi:
            if rsi < 30:
                analysis_parts.append(f"RSI {rsi:.1f} indicates oversold conditions.")
            elif rsi > 70:
                analysis_parts.append(f"RSI {rsi:.1f} suggests overbought levels.")
            else:
                analysis_parts.append(f"RSI {rsi:.1f} in neutral zone.")
        
        # Trend analysis
        if current_price and sma20 and sma50:
            if current_price > sma20 > sma50:
                analysis_parts.append("Strong uptrend with price above key moving averages.")
            elif current_price < sma20 < sma50:
                analysis_parts.append("Downtrend with price below moving averages.")
            else:
                analysis_parts.append("Mixed trend signals from moving averages.")
        
        # MACD analysis
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                analysis_parts.append("MACD showing bullish momentum.")
            else:
                analysis_parts.append("MACD indicating bearish momentum.")
        
        # Bollinger Bands analysis
        bb_upper = indicators.get('bb_upper')
        bb_lower = indicators.get('bb_lower')
        if current_price and bb_upper and bb_lower:
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
            if bb_position > 0.8:
                analysis_parts.append("Price near upper Bollinger Band - potential resistance.")
            elif bb_position < 0.2:
                analysis_parts.append("Price near lower Bollinger Band - potential support.")
        
        return " ".join(analysis_parts)
    
    def _extract_key_metrics(self, indicators: Dict[str, Any], price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key technical metrics"""
        metrics = {
            'current_price': indicators.get('current_price'),
            'rsi14': indicators.get('rsi14'),
            'sma20': indicators.get('sma20'),
            'sma50': indicators.get('sma50'),
            'sma200': indicators.get('sma200'),
            'macd': indicators.get('macd'),
            'macd_signal': indicators.get('macd_signal'),
            'bb_upper': indicators.get('bb_upper'),
            'bb_middle': indicators.get('bb_middle'),
            'bb_lower': indicators.get('bb_lower')
        }
        
        if "error" not in price_data:
            metrics.update({
                'high_52w': price_data.get('high_52w'),
                'low_52w': price_data.get('low_52w'),
                'volume_avg': price_data.get('volume_avg')
            })
        
        return metrics
    
    def _calculate_confidence(self, indicators: Dict[str, Any]) -> float:
        """Calculate confidence based on data availability"""
        key_indicators = ['rsi14', 'sma20', 'sma50', 'macd', 'bb_upper']
        available_indicators = sum(1 for indicator in key_indicators if indicators.get(indicator) is not None)
        return min(0.95, 0.6 + (available_indicators / len(key_indicators)) * 0.3)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "error": error_msg,
            "scores": {},
            "overall_score": 0.5,
            "analysis": f"Unable to perform technical analysis: {error_msg}",
            "key_metrics": {},
            "recommendation_signal": "HOLD",
            "confidence": 0.1,
            "timestamp": datetime.now().isoformat()
        }