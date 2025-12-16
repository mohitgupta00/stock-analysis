import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent
from typing import Dict, Any
import requests
from datetime import datetime

class MacroContextAgent(BaseAgent):
    """Agent for macroeconomic context analysis"""
    
    def __init__(self):
        super().__init__("Macro_Context_Agent", weight=0.15)
        
        # Sector sensitivity to macro factors
        self.sector_sensitivities = {
            'Technology': {'interest_rates': -0.3, 'gdp_growth': 0.4, 'inflation': -0.2, 'currency': 0.3},
            'Banking': {'interest_rates': 0.5, 'gdp_growth': 0.6, 'inflation': -0.3, 'currency': 0.1},
            'Energy': {'interest_rates': -0.2, 'gdp_growth': 0.3, 'inflation': 0.4, 'currency': 0.2},
            'Consumer': {'interest_rates': -0.4, 'gdp_growth': 0.5, 'inflation': -0.5, 'currency': -0.1},
            'Healthcare': {'interest_rates': -0.1, 'gdp_growth': 0.2, 'inflation': -0.1, 'currency': 0.1},
            'Industrials': {'interest_rates': -0.3, 'gdp_growth': 0.7, 'inflation': -0.3, 'currency': 0.2},
            'Materials': {'interest_rates': -0.2, 'gdp_growth': 0.6, 'inflation': 0.3, 'currency': 0.3}
        }
        
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform macroeconomic context analysis"""
        try:
            # Get stock sector info
            from data.pricefetcher import PriceFetcher
            fetcher = PriceFetcher()
            fundamentals = fetcher.fetch_fundamentals(ticker)
            
            sector = fundamentals.get('sector', 'Unknown')
            
            # Get macro indicators (using mock data for now - can be replaced with real APIs)
            macro_data = self._get_macro_indicators()
            
            # Calculate macro impact scores
            scores = self._calculate_macro_scores(sector, macro_data)
            
            # Generate analysis
            analysis = self._generate_analysis(sector, macro_data, scores)
            
            return self.create_response(
                scores=scores,
                analysis=analysis,
                key_metrics=self._extract_key_metrics(macro_data, sector),
                confidence=self._calculate_confidence(macro_data)
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _get_macro_indicators(self) -> Dict[str, Any]:
        """Get macroeconomic indicators (mock data for now)"""
        # In production, this would fetch from RBI, World Bank, etc.
        # For now, using reasonable current estimates
        
        return {
            'india_gdp_growth': 6.2,  # % annual
            'inflation_rate': 4.8,   # % annual
            'repo_rate': 6.5,        # RBI repo rate %
            'usd_inr_rate': 83.2,    # Current USD/INR
            'usd_inr_volatility': 0.8,  # % monthly volatility
            'global_it_spending_growth': 6.5,  # % for IT sector
            'crude_oil_price': 75,   # USD per barrel
            'global_sentiment': 'POSITIVE',  # POSITIVE/NEUTRAL/NEGATIVE
            'india_market_sentiment': 'BULLISH',  # BULLISH/NEUTRAL/BEARISH
            'fii_flows': 'POSITIVE',  # Foreign investment flows
            'monsoon_forecast': 'NORMAL'  # For agriculture-dependent sectors
        }
    
    def _calculate_macro_scores(self, sector: str, macro_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate macro impact scores"""
        scores = {}
        
        # GDP Growth Impact Score
        gdp_growth = macro_data.get('india_gdp_growth', 6.0)
        gdp_score = 0.5
        
        if gdp_growth >= 7.0:  # Strong growth
            gdp_score = 0.8
        elif gdp_growth >= 6.0:  # Moderate growth
            gdp_score = 0.7
        elif gdp_growth >= 5.0:  # Slow growth
            gdp_score = 0.5
        else:  # Weak growth
            gdp_score = 0.3
        
        # Adjust for sector sensitivity
        sector_sensitivity = self.sector_sensitivities.get(sector, {})
        gdp_sensitivity = sector_sensitivity.get('gdp_growth', 0.3)
        gdp_score = 0.5 + (gdp_score - 0.5) * abs(gdp_sensitivity)
        
        scores['gdp_impact_score'] = max(0, min(1, gdp_score))
        
        # Interest Rate Impact Score
        repo_rate = macro_data.get('repo_rate', 6.5)
        interest_score = 0.5
        
        if repo_rate <= 5.0:  # Low rates - generally positive
            interest_score = 0.7
        elif repo_rate <= 6.5:  # Moderate rates
            interest_score = 0.6
        elif repo_rate <= 8.0:  # High rates
            interest_score = 0.4
        else:  # Very high rates
            interest_score = 0.3
        
        # Adjust for sector sensitivity (negative sensitivity means inverse relationship)
        interest_sensitivity = sector_sensitivity.get('interest_rates', 0)
        if interest_sensitivity < 0:  # Negative sensitivity (like tech, consumer)
            interest_score = 1 - interest_score + 0.5
        
        scores['interest_rate_impact_score'] = max(0, min(1, interest_score))
        
        # Inflation Impact Score
        inflation = macro_data.get('inflation_rate', 4.8)
        inflation_score = 0.5
        
        if inflation <= 4.0:  # Low inflation - good
            inflation_score = 0.7
        elif inflation <= 6.0:  # Moderate inflation - RBI target range
            inflation_score = 0.6
        elif inflation <= 8.0:  # High inflation
            inflation_score = 0.4
        else:  # Very high inflation
            inflation_score = 0.2
        
        scores['inflation_impact_score'] = inflation_score
        
        # Currency Impact Score (for export-oriented sectors)
        usd_inr = macro_data.get('usd_inr_rate', 83.0)
        currency_volatility = macro_data.get('usd_inr_volatility', 1.0)
        
        currency_score = 0.5
        
        # Higher USD/INR generally good for IT/export sectors
        if sector == 'Technology':
            if usd_inr >= 82:  # Favorable for IT exports
                currency_score = 0.7
            elif usd_inr <= 78:  # Less favorable
                currency_score = 0.4
        
        # Lower volatility is generally better
        if currency_volatility <= 0.5:
            currency_score += 0.1
        elif currency_volatility >= 2.0:
            currency_score -= 0.1
        
        scores['currency_impact_score'] = max(0, min(1, currency_score))
        
        # Market Sentiment Score
        market_sentiment = macro_data.get('india_market_sentiment', 'NEUTRAL')
        fii_flows = macro_data.get('fii_flows', 'NEUTRAL')
        
        sentiment_score = 0.5
        
        if market_sentiment == 'BULLISH':
            sentiment_score += 0.2
        elif market_sentiment == 'BEARISH':
            sentiment_score -= 0.2
        
        if fii_flows == 'POSITIVE':
            sentiment_score += 0.1
        elif fii_flows == 'NEGATIVE':
            sentiment_score -= 0.1
        
        scores['market_sentiment_score'] = max(0, min(1, sentiment_score))
        
        return scores
    
    def _generate_analysis(self, sector: str, macro_data: Dict[str, Any], scores: Dict[str, float]) -> str:
        """Generate macro context analysis"""
        
        gdp_growth = macro_data.get('india_gdp_growth', 6.0)
        inflation = macro_data.get('inflation_rate', 4.8)
        repo_rate = macro_data.get('repo_rate', 6.5)
        
        analysis_parts = []
        
        # GDP context
        if gdp_growth >= 6.5:
            analysis_parts.append(f"Strong GDP growth ({gdp_growth}%) supports economic expansion.")
        elif gdp_growth >= 5.5:
            analysis_parts.append(f"Moderate GDP growth ({gdp_growth}%) provides stable backdrop.")
        else:
            analysis_parts.append(f"Slower GDP growth ({gdp_growth}%) may constrain performance.")
        
        # Inflation context
        if inflation <= 4.0:
            analysis_parts.append("Low inflation environment favorable for consumption.")
        elif inflation <= 6.0:
            analysis_parts.append("Inflation within RBI comfort zone.")
        else:
            analysis_parts.append("Elevated inflation poses headwinds.")
        
        # Interest rate context
        if repo_rate <= 6.0:
            analysis_parts.append("Accommodative monetary policy supports growth.")
        elif repo_rate >= 7.0:
            analysis_parts.append("Tight monetary policy may constrain expansion.")
        else:
            analysis_parts.append("Neutral monetary policy stance.")
        
        # Sector-specific context
        if sector == 'Technology':
            usd_inr = macro_data.get('usd_inr_rate', 83.0)
            it_growth = macro_data.get('global_it_spending_growth', 6.5)
            analysis_parts.append(f"IT sector benefits from USD/INR at {usd_inr} and global IT spending growth of {it_growth}%.")
        
        elif sector == 'Banking':
            analysis_parts.append("Banking sector positioned to benefit from economic growth and stable rates.")
        
        elif sector == 'Energy':
            oil_price = macro_data.get('crude_oil_price', 75)
            analysis_parts.append(f"Energy sector impacted by crude oil at ${oil_price}/barrel.")
        
        # Market sentiment
        market_sentiment = macro_data.get('india_market_sentiment', 'NEUTRAL')
        fii_flows = macro_data.get('fii_flows', 'NEUTRAL')
        
        if market_sentiment == 'BULLISH' and fii_flows == 'POSITIVE':
            analysis_parts.append("Positive market sentiment and FII inflows provide tailwinds.")
        elif market_sentiment == 'BEARISH' or fii_flows == 'NEGATIVE':
            analysis_parts.append("Market headwinds from sentiment or foreign outflows.")
        
        return " ".join(analysis_parts)
    
    def _extract_key_metrics(self, macro_data: Dict[str, Any], sector: str) -> Dict[str, Any]:
        """Extract key macro metrics"""
        return {
            'gdp_growth': macro_data.get('india_gdp_growth'),
            'inflation_rate': macro_data.get('inflation_rate'),
            'repo_rate': macro_data.get('repo_rate'),
            'usd_inr_rate': macro_data.get('usd_inr_rate'),
            'market_sentiment': macro_data.get('india_market_sentiment'),
            'fii_flows': macro_data.get('fii_flows'),
            'sector': sector,
            'global_it_spending_growth': macro_data.get('global_it_spending_growth'),
            'crude_oil_price': macro_data.get('crude_oil_price')
        }
    
    def _calculate_confidence(self, macro_data: Dict[str, Any]) -> float:
        """Calculate confidence based on data availability"""
        key_indicators = ['india_gdp_growth', 'inflation_rate', 'repo_rate', 'usd_inr_rate']
        available_indicators = sum(1 for indicator in key_indicators if macro_data.get(indicator) is not None)
        return min(0.85, 0.5 + (available_indicators / len(key_indicators)) * 0.3)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "error": error_msg,
            "scores": {},
            "overall_score": 0.5,
            "analysis": f"Unable to perform macro analysis: {error_msg}",
            "key_metrics": {},
            "recommendation_signal": "HOLD",
            "confidence": 0.1,
            "timestamp": datetime.now().isoformat()
        }