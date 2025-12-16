import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent
from data.pricefetcher import PriceFetcher
from typing import Dict, Any
import pandas as pd

class FundamentalAnalysisAgent(BaseAgent):
    """Agent for fundamental analysis - valuation, profitability, financial health"""
    
    def __init__(self):
        super().__init__("Fundamental_Analysis_Agent", weight=0.30)
        self.fetcher = PriceFetcher()
        
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fundamental analysis"""
        try:
            # Get fundamental data
            fundamentals = self.fetcher.fetch_fundamentals(ticker)
            
            if "error" in fundamentals:
                return self._create_error_response(fundamentals["error"])
            
            # Calculate scores
            scores = self._calculate_fundamental_scores(fundamentals)
            
            # Generate analysis
            analysis = self._generate_analysis(fundamentals, scores, context.get('user_preference', 'balanced'))
            
            return self.create_response(
                scores=scores,
                analysis=analysis,
                key_metrics=self._extract_key_metrics(fundamentals),
                confidence=self._calculate_confidence(fundamentals)
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _calculate_fundamental_scores(self, fundamentals: Dict[str, Any]) -> Dict[str, float]:
        """Calculate fundamental analysis scores"""
        scores = {}
        
        # Valuation Score (P/E, P/B ratios)
        pe_ratio = fundamentals.get('pe_ratio')
        pb_ratio = fundamentals.get('pb_ratio')
        
        valuation_score = 0.5  # neutral
        if pe_ratio:
            if 10 <= pe_ratio <= 20:  # Good P/E range
                valuation_score += 0.3
            elif pe_ratio < 10:  # Very cheap
                valuation_score += 0.4
            elif pe_ratio > 30:  # Expensive
                valuation_score -= 0.2
        
        if pb_ratio:
            if 1 <= pb_ratio <= 3:  # Reasonable P/B
                valuation_score += 0.2
            elif pb_ratio < 1:  # Undervalued
                valuation_score += 0.3
        
        scores['valuation_score'] = max(0, min(1, valuation_score))
        
        # Profitability Score (ROE, Margins)
        roe = fundamentals.get('roe')
        profit_margin = fundamentals.get('profit_margin')
        
        profitability_score = 0.5
        if roe and roe > 0:
            if roe >= 0.15:  # 15%+ ROE is good
                profitability_score += 0.3
            elif roe >= 0.10:  # 10%+ ROE is decent
                profitability_score += 0.2
        
        if profit_margin and profit_margin > 0:
            if profit_margin >= 0.15:  # 15%+ margin is good
                profitability_score += 0.2
            elif profit_margin >= 0.10:  # 10%+ margin is decent
                profitability_score += 0.1
        
        scores['profitability_score'] = max(0, min(1, profitability_score))
        
        # Financial Health Score (Debt/Equity)
        debt_to_equity = fundamentals.get('debt_to_equity')
        
        financial_health_score = 0.7  # assume good by default
        if debt_to_equity is not None:
            if debt_to_equity <= 0.3:  # Low debt is good
                financial_health_score = 0.9
            elif debt_to_equity <= 0.6:  # Moderate debt
                financial_health_score = 0.7
            elif debt_to_equity <= 1.0:  # High debt
                financial_health_score = 0.5
            else:  # Very high debt
                financial_health_score = 0.3
        
        scores['financial_health_score'] = financial_health_score
        
        # Growth Score (Revenue Growth)
        revenue_growth = fundamentals.get('revenue_growth')
        
        growth_score = 0.5
        if revenue_growth:
            if revenue_growth >= 0.15:  # 15%+ growth is excellent
                growth_score = 0.9
            elif revenue_growth >= 0.10:  # 10%+ growth is good
                growth_score = 0.7
            elif revenue_growth >= 0.05:  # 5%+ growth is decent
                growth_score = 0.6
            elif revenue_growth < 0:  # Negative growth
                growth_score = 0.3
        
        scores['growth_score'] = growth_score
        
        return scores
    
    def _generate_analysis(self, fundamentals: Dict[str, Any], scores: Dict[str, float], 
                          user_preference: str) -> str:
        """Generate fundamental analysis text"""
        
        pe_ratio = fundamentals.get('pe_ratio', 'N/A')
        roe = fundamentals.get('roe', 'N/A')
        debt_equity = fundamentals.get('debt_to_equity', 'N/A')
        revenue_growth = fundamentals.get('revenue_growth', 'N/A')
        
        # Format percentages
        if isinstance(roe, (int, float)):
            roe = f"{roe*100:.1f}%"
        if isinstance(revenue_growth, (int, float)):
            revenue_growth = f"{revenue_growth*100:.1f}%"
        
        analysis_parts = []
        
        # Valuation assessment
        if scores['valuation_score'] >= 0.7:
            analysis_parts.append("Attractive valuation metrics.")
        elif scores['valuation_score'] <= 0.4:
            analysis_parts.append("Expensive valuation - trading at premium.")
        else:
            analysis_parts.append("Fair valuation.")
        
        # Profitability assessment
        if scores['profitability_score'] >= 0.7:
            analysis_parts.append("Strong profitability with good ROE and margins.")
        elif scores['profitability_score'] <= 0.4:
            analysis_parts.append("Weak profitability metrics.")
        else:
            analysis_parts.append("Moderate profitability.")
        
        # Financial health
        if scores['financial_health_score'] >= 0.8:
            analysis_parts.append("Excellent balance sheet with low debt.")
        elif scores['financial_health_score'] <= 0.5:
            analysis_parts.append("High debt levels pose financial risk.")
        else:
            analysis_parts.append("Reasonable financial health.")
        
        # Growth prospects
        if scores['growth_score'] >= 0.7:
            analysis_parts.append("Strong revenue growth trajectory.")
        elif scores['growth_score'] <= 0.4:
            analysis_parts.append("Weak or declining growth.")
        else:
            analysis_parts.append("Moderate growth prospects.")
        
        base_analysis = " ".join(analysis_parts)
        
        # Add user preference context
        if user_preference == 'value':
            if scores['valuation_score'] >= 0.7:
                base_analysis += " Good fit for value investing strategy."
            else:
                base_analysis += " May not suit strict value investing criteria."
        elif user_preference == 'growth':
            if scores['growth_score'] >= 0.7:
                base_analysis += " Aligns well with growth investing approach."
            else:
                base_analysis += " Limited growth potential for growth investors."
        
        return f"P/E: {pe_ratio}, ROE: {roe}, D/E: {debt_equity}, Growth: {revenue_growth}. {base_analysis}"
    
    def _extract_key_metrics(self, fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key fundamental metrics"""
        return {
            'pe_ratio': fundamentals.get('pe_ratio'),
            'pb_ratio': fundamentals.get('pb_ratio'),
            'roe': fundamentals.get('roe'),
            'debt_to_equity': fundamentals.get('debt_to_equity'),
            'profit_margin': fundamentals.get('profit_margin'),
            'revenue_growth': fundamentals.get('revenue_growth'),
            'market_cap': fundamentals.get('market_cap'),
            'sector': fundamentals.get('sector')
        }
    
    def _calculate_confidence(self, fundamentals: Dict[str, Any]) -> float:
        """Calculate confidence based on data availability"""
        key_metrics = ['pe_ratio', 'roe', 'debt_to_equity', 'profit_margin']
        available_metrics = sum(1 for metric in key_metrics if fundamentals.get(metric) is not None)
        return min(0.95, 0.5 + (available_metrics / len(key_metrics)) * 0.4)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "error": error_msg,
            "scores": {},
            "overall_score": 0.5,
            "analysis": f"Unable to perform fundamental analysis: {error_msg}",
            "key_metrics": {},
            "recommendation_signal": "HOLD",
            "confidence": 0.1,
            "timestamp": datetime.now().isoformat()
        }