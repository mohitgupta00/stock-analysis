import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent
from data.pricefetcher import PriceFetcher
from typing import Dict, Any
import yfinance as yf
import numpy as np
from datetime import datetime

class RiskAssessmentAgent(BaseAgent):
    """Agent for risk assessment and safety margin analysis"""
    
    def __init__(self):
        super().__init__("Risk_Assessment_Agent", weight=0.15)
        self.fetcher = PriceFetcher()
        
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform risk assessment analysis"""
        try:
            # Get fundamental and price data
            fundamentals = self.fetcher.fetch_fundamentals(ticker)
            price_data = self.fetcher.fetch_price_data(ticker)
            
            if "error" in fundamentals or "error" in price_data:
                return self._create_error_response("Unable to fetch required data for risk analysis")
            
            # Get historical data for volatility analysis
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2y")  # 2 years for better volatility estimate
            
            # Calculate risk scores
            scores = self._calculate_risk_scores(fundamentals, price_data, hist)
            
            # Generate analysis
            analysis = self._generate_analysis(fundamentals, price_data, hist, scores, 
                                             context.get('user_preference', 'balanced'))
            
            return self.create_response(
                scores=scores,
                analysis=analysis,
                key_metrics=self._extract_key_metrics(fundamentals, price_data, hist),
                confidence=self._calculate_confidence(fundamentals, hist)
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _calculate_risk_scores(self, fundamentals: Dict[str, Any], 
                              price_data: Dict[str, Any], hist) -> Dict[str, float]:
        """Calculate various risk assessment scores"""
        scores = {}
        
        # Valuation Risk Score
        pe_ratio = fundamentals.get('pe_ratio')
        pb_ratio = fundamentals.get('pb_ratio')
        
        valuation_risk_score = 0.5  # Lower score = higher risk
        
        if pe_ratio:
            if pe_ratio <= 15:  # Low valuation risk
                valuation_risk_score += 0.3
            elif pe_ratio <= 25:  # Moderate valuation risk
                valuation_risk_score += 0.1
            elif pe_ratio >= 40:  # High valuation risk
                valuation_risk_score -= 0.3
            elif pe_ratio >= 30:  # Elevated valuation risk
                valuation_risk_score -= 0.1
        
        if pb_ratio:
            if pb_ratio <= 2:  # Low book value risk
                valuation_risk_score += 0.2
            elif pb_ratio >= 5:  # High book value risk
                valuation_risk_score -= 0.2
        
        scores['valuation_risk_score'] = max(0, min(1, valuation_risk_score))
        
        # Financial Risk Score (Debt levels)
        debt_to_equity = fundamentals.get('debt_to_equity')
        
        financial_risk_score = 0.7  # Assume moderate risk by default
        
        if debt_to_equity is not None:
            if debt_to_equity <= 0.3:  # Low financial risk
                financial_risk_score = 0.9
            elif debt_to_equity <= 0.6:  # Moderate financial risk
                financial_risk_score = 0.7
            elif debt_to_equity <= 1.0:  # High financial risk
                financial_risk_score = 0.4
            else:  # Very high financial risk
                financial_risk_score = 0.2
        
        scores['financial_risk_score'] = financial_risk_score
        
        # Volatility Risk Score
        volatility_risk_score = 0.5
        
        if not hist.empty and len(hist) >= 252:  # At least 1 year of data
            # Calculate annualized volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            if volatility <= 0.20:  # Low volatility (<=20%)
                volatility_risk_score = 0.8
            elif volatility <= 0.35:  # Moderate volatility (<=35%)
                volatility_risk_score = 0.6
            elif volatility <= 0.50:  # High volatility (<=50%)
                volatility_risk_score = 0.4
            else:  # Very high volatility (>50%)
                volatility_risk_score = 0.2
        
        scores['volatility_risk_score'] = volatility_risk_score
        
        # Liquidity Risk Score (based on market cap and volume)
        market_cap = fundamentals.get('market_cap', 0)
        avg_volume = price_data.get('volume_avg', 0)
        
        liquidity_risk_score = 0.5
        
        if market_cap >= 100000000000:  # Large cap (>1000 Cr) - low liquidity risk
            liquidity_risk_score = 0.8
        elif market_cap >= 50000000000:  # Mid cap (>500 Cr) - moderate liquidity risk
            liquidity_risk_score = 0.6
        elif market_cap >= 10000000000:  # Small cap (>100 Cr) - higher liquidity risk
            liquidity_risk_score = 0.4
        else:  # Micro cap - high liquidity risk
            liquidity_risk_score = 0.3
        
        # Adjust for trading volume
        if avg_volume and avg_volume > 1000000:  # High volume
            liquidity_risk_score = min(1.0, liquidity_risk_score + 0.1)
        elif avg_volume and avg_volume < 100000:  # Low volume
            liquidity_risk_score = max(0.1, liquidity_risk_score - 0.2)
        
        scores['liquidity_risk_score'] = liquidity_risk_score
        
        # Safety Margin Score (intrinsic value estimation)
        safety_margin_score = self._calculate_safety_margin_score(fundamentals, price_data)
        scores['safety_margin_score'] = safety_margin_score
        
        # Downside Risk Score (based on 52-week performance)
        downside_risk_score = self._calculate_downside_risk_score(price_data, hist)
        scores['downside_risk_score'] = downside_risk_score
        
        return scores
    
    def _calculate_safety_margin_score(self, fundamentals: Dict[str, Any], 
                                      price_data: Dict[str, Any]) -> float:
        """Calculate safety margin based on simple valuation models"""
        
        current_price = price_data.get('current_price', 0)
        pe_ratio = fundamentals.get('pe_ratio')
        roe = fundamentals.get('roe')
        
        if not current_price or not pe_ratio:
            return 0.5  # Neutral if insufficient data
        
        # Simple intrinsic value estimation using P/E normalization
        # Assume fair P/E based on ROE and growth
        fair_pe = 15  # Base fair P/E
        
        if roe:
            if roe >= 0.20:  # High ROE deserves premium
                fair_pe = 20
            elif roe >= 0.15:  # Good ROE
                fair_pe = 18
            elif roe <= 0.10:  # Low ROE deserves discount
                fair_pe = 12
        
        # Estimate intrinsic value
        estimated_eps = current_price / pe_ratio
        intrinsic_value = estimated_eps * fair_pe
        
        # Calculate safety margin
        if intrinsic_value > 0:
            safety_margin = (intrinsic_value - current_price) / intrinsic_value
            
            if safety_margin >= 0.30:  # 30%+ safety margin
                return 0.9
            elif safety_margin >= 0.20:  # 20%+ safety margin
                return 0.8
            elif safety_margin >= 0.10:  # 10%+ safety margin
                return 0.7
            elif safety_margin >= 0:  # Fair value
                return 0.6
            elif safety_margin >= -0.20:  # Mild overvaluation
                return 0.4
            else:  # Significant overvaluation
                return 0.2
        
        return 0.5
    
    def _calculate_downside_risk_score(self, price_data: Dict[str, Any], hist) -> float:
        """Calculate downside risk based on historical performance"""
        
        current_price = price_data.get('current_price', 0)
        low_52w = price_data.get('low_52w', 0)
        high_52w = price_data.get('high_52w', 0)
        
        downside_risk_score = 0.5
        
        if current_price and low_52w and high_52w:
            # Position in 52-week range
            range_position = (current_price - low_52w) / (high_52w - low_52w)
            
            if range_position >= 0.8:  # Near 52-week high - higher downside risk
                downside_risk_score = 0.3
            elif range_position >= 0.6:  # Upper range - moderate downside risk
                downside_risk_score = 0.5
            elif range_position >= 0.4:  # Middle range - balanced risk
                downside_risk_score = 0.6
            elif range_position >= 0.2:  # Lower range - lower downside risk
                downside_risk_score = 0.7
            else:  # Near 52-week low - lowest downside risk
                downside_risk_score = 0.8
        
        # Adjust based on historical drawdowns
        if not hist.empty and len(hist) >= 252:
            returns = hist['Close'].pct_change().dropna()
            
            # Calculate maximum drawdown
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = abs(drawdown.min())
            
            if max_drawdown <= 0.20:  # Low historical drawdown
                downside_risk_score = min(1.0, downside_risk_score + 0.1)
            elif max_drawdown >= 0.50:  # High historical drawdown
                downside_risk_score = max(0.1, downside_risk_score - 0.2)
        
        return downside_risk_score
    
    def _generate_analysis(self, fundamentals: Dict[str, Any], price_data: Dict[str, Any], 
                          hist, scores: Dict[str, float], user_preference: str) -> str:
        """Generate risk assessment analysis"""
        
        analysis_parts = []
        
        # Valuation risk
        valuation_risk = scores.get('valuation_risk_score', 0.5)
        if valuation_risk >= 0.7:
            analysis_parts.append("Low valuation risk with reasonable P/E and P/B ratios.")
        elif valuation_risk <= 0.4:
            analysis_parts.append("High valuation risk - trading at expensive multiples.")
        else:
            analysis_parts.append("Moderate valuation risk.")
        
        # Financial risk
        financial_risk = scores.get('financial_risk_score', 0.5)
        debt_to_equity = fundamentals.get('debt_to_equity')
        if financial_risk >= 0.8:
            analysis_parts.append("Strong balance sheet with low debt levels.")
        elif financial_risk <= 0.4:
            analysis_parts.append(f"High financial risk with D/E ratio of {debt_to_equity:.2f}." if debt_to_equity else "High financial risk from debt levels.")
        else:
            analysis_parts.append("Moderate financial risk.")
        
        # Volatility risk
        volatility_risk = scores.get('volatility_risk_score', 0.5)
        if volatility_risk >= 0.7:
            analysis_parts.append("Low price volatility indicates stable stock.")
        elif volatility_risk <= 0.4:
            analysis_parts.append("High price volatility suggests elevated risk.")
        else:
            analysis_parts.append("Moderate price volatility.")
        
        # Safety margin
        safety_margin = scores.get('safety_margin_score', 0.5)
        if safety_margin >= 0.7:
            analysis_parts.append("Adequate safety margin for value investors.")
        elif safety_margin <= 0.4:
            analysis_parts.append("Limited safety margin - potential overvaluation.")
        else:
            analysis_parts.append("Fair valuation with moderate safety margin.")
        
        # Downside risk
        downside_risk = scores.get('downside_risk_score', 0.5)
        current_price = price_data.get('current_price', 0)
        low_52w = price_data.get('low_52w', 0)
        
        if downside_risk >= 0.7:
            analysis_parts.append("Limited downside risk from current levels.")
        elif downside_risk <= 0.4:
            analysis_parts.append("Elevated downside risk - price near recent highs.")
        
        if current_price and low_52w:
            downside_to_52w_low = ((current_price - low_52w) / current_price) * 100
            analysis_parts.append(f"Potential downside to 52-week low: {downside_to_52w_low:.1f}%.")
        
        # User preference context
        if user_preference == 'value':
            if safety_margin >= 0.7 and valuation_risk >= 0.6:
                analysis_parts.append("Risk profile suitable for value investing approach.")
            else:
                analysis_parts.append("Risk-reward may not favor value investing strategy.")
        elif user_preference == 'growth':
            if volatility_risk >= 0.5:  # Growth investors may accept higher volatility
                analysis_parts.append("Risk levels acceptable for growth-oriented investors.")
            else:
                analysis_parts.append("High volatility may concern growth investors.")
        
        return " ".join(analysis_parts)
    
    def _extract_key_metrics(self, fundamentals: Dict[str, Any], 
                            price_data: Dict[str, Any], hist) -> Dict[str, Any]:
        """Extract key risk metrics"""
        
        metrics = {
            'current_price': price_data.get('current_price'),
            'pe_ratio': fundamentals.get('pe_ratio'),
            'debt_to_equity': fundamentals.get('debt_to_equity'),
            'market_cap': fundamentals.get('market_cap'),
            'high_52w': price_data.get('high_52w'),
            'low_52w': price_data.get('low_52w'),
            'volume_avg': price_data.get('volume_avg')
        }
        
        # Calculate additional risk metrics
        if not hist.empty and len(hist) >= 252:
            returns = hist['Close'].pct_change().dropna()
            metrics['annualized_volatility'] = returns.std() * np.sqrt(252)
            
            # Maximum drawdown
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            metrics['max_drawdown'] = abs(drawdown.min())
        
        # Safety margin calculation
        current_price = price_data.get('current_price', 0)
        pe_ratio = fundamentals.get('pe_ratio')
        
        if current_price and pe_ratio:
            estimated_eps = current_price / pe_ratio
            fair_pe = 15  # Conservative estimate
            intrinsic_value = estimated_eps * fair_pe
            metrics['estimated_intrinsic_value'] = intrinsic_value
            metrics['safety_margin_percent'] = ((intrinsic_value - current_price) / intrinsic_value * 100) if intrinsic_value > 0 else None
        
        return metrics
    
    def _calculate_confidence(self, fundamentals: Dict[str, Any], hist) -> float:
        """Calculate confidence based on data availability"""
        
        key_metrics = ['pe_ratio', 'debt_to_equity', 'market_cap']
        available_metrics = sum(1 for metric in key_metrics if fundamentals.get(metric) is not None)
        
        data_quality_factor = available_metrics / len(key_metrics)
        
        # Historical data availability
        history_factor = 1.0 if not hist.empty and len(hist) >= 252 else 0.5
        
        return min(0.9, 0.4 + data_quality_factor * 0.3 + history_factor * 0.2)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "error": error_msg,
            "scores": {},
            "overall_score": 0.5,
            "analysis": f"Unable to perform risk assessment: {error_msg}",
            "key_metrics": {},
            "recommendation_signal": "HOLD",
            "confidence": 0.1,
            "timestamp": datetime.now().isoformat()
        }