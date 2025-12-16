import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_agent import FundamentalAnalysisAgent
from agents.technical_agent import TechnicalAnalysisAgent
from agents.peer_comparison_agent import PeerComparisonAgent
from agents.macro_context_agent import MacroContextAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from typing import Dict, Any, List
from datetime import datetime
import asyncio

class MultiAgentOrchestrator:
    """Orchestrates multiple analysis agents for comprehensive stock analysis"""
    
    def __init__(self):
        # Initialize all agents
        self.agents = {
            'fundamental': FundamentalAnalysisAgent(),
            'technical': TechnicalAnalysisAgent(),
            'peer_comparison': PeerComparisonAgent(),
            'macro_context': MacroContextAgent(),
            'risk_assessment': RiskAssessmentAgent()
        }
        
        # Agent weights (should sum to 1.0)
        self.weights = {
            'fundamental': 0.30,
            'technical': 0.25,
            'peer_comparison': 0.15,
            'macro_context': 0.15,
            'risk_assessment': 0.15
        }
        
    def analyze_stock(self, ticker: str, user_query: str = "", user_preference: str = "balanced") -> Dict[str, Any]:
        """Perform comprehensive multi-agent analysis"""
        
        # Prepare context for agents
        context = {
            'user_query': user_query,
            'user_preference': user_preference,  # 'value', 'growth', 'balanced'
            'ticker': ticker,
            'timestamp': datetime.now().isoformat()
        }
        
        # Determine which agents to use based on query
        active_agents = self._determine_active_agents(user_query)
        
        # Run agent analysis
        agent_results = {}
        
        for agent_name in active_agents:
            if agent_name in self.agents:
                try:
                    print(f"Running {agent_name} analysis for {ticker}...")
                    result = self.agents[agent_name].analyze(ticker, context)
                    agent_results[agent_name] = result
                except Exception as e:
                    print(f"Error in {agent_name}: {e}")
                    agent_results[agent_name] = self._create_agent_error(agent_name, str(e))
        
        # Aggregate results
        final_recommendation = self._aggregate_agent_results(agent_results, active_agents)
        
        # Add metadata
        final_recommendation.update({
            'ticker': ticker,
            'user_query': user_query,
            'user_preference': user_preference,
            'active_agents': active_agents,
            'agent_results': agent_results,
            'analysis_timestamp': datetime.now().isoformat()
        })
        
        return final_recommendation
    
    def _determine_active_agents(self, user_query: str) -> List[str]:
        """Determine which agents to activate based on user query"""
        
        query_lower = user_query.lower()
        
        # Default: use all agents
        active_agents = ['fundamental', 'technical', 'peer_comparison', 'macro_context', 'risk_assessment']
        
        # Query-specific agent selection
        if any(word in query_lower for word in ['fundamental', 'valuation', 'p/e', 'financial', 'balance sheet']):
            # Fundamental-focused query
            active_agents = ['fundamental', 'peer_comparison', 'risk_assessment']
            
        elif any(word in query_lower for word in ['technical', 'chart', 'trend', 'momentum', 'rsi', 'macd']):
            # Technical-focused query
            active_agents = ['technical', 'risk_assessment']
            
        elif any(word in query_lower for word in ['compare', 'peer', 'sector', 'vs', 'against']):
            # Comparison-focused query
            active_agents = ['fundamental', 'peer_comparison', 'technical']
            
        elif any(word in query_lower for word in ['macro', 'economy', 'gdp', 'inflation', 'interest rate']):
            # Macro-focused query
            active_agents = ['macro_context', 'fundamental', 'risk_assessment']
            
        elif any(word in query_lower for word in ['risk', 'safe', 'downside', 'volatility']):
            # Risk-focused query
            active_agents = ['risk_assessment', 'fundamental', 'technical']
            
        elif any(word in query_lower for word in ['buy', 'sell', 'invest', 'recommendation']):
            # Investment recommendation - use all agents
            active_agents = ['fundamental', 'technical', 'peer_comparison', 'macro_context', 'risk_assessment']
        
        return active_agents
    
    def _aggregate_agent_results(self, agent_results: Dict[str, Any], active_agents: List[str]) -> Dict[str, Any]:
        """Aggregate results from multiple agents into final recommendation"""
        
        # Calculate weighted scores
        total_weighted_score = 0
        total_weight = 0
        agent_scores = {}
        
        for agent_name in active_agents:
            if agent_name in agent_results and 'overall_score' in agent_results[agent_name]:
                score = agent_results[agent_name]['overall_score']
                weight = self.weights[agent_name]
                
                agent_scores[agent_name] = score
                total_weighted_score += score * weight
                total_weight += weight
        
        # Final weighted score
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0.5
        
        # Determine final recommendation
        final_signal = self._get_final_recommendation_signal(final_score, agent_results)
        
        # Calculate confidence
        confidence = self._calculate_overall_confidence(agent_results, active_agents)
        
        # Generate summary analysis
        summary_analysis = self._generate_summary_analysis(agent_results, final_score, final_signal)
        
        return {
            'recommendation': {
                'signal': final_signal,
                'score': round(final_score, 3),
                'confidence': round(confidence, 3)
            },
            'agent_scores': agent_scores,
            'summary_analysis': summary_analysis,
            'key_insights': self._extract_key_insights(agent_results),
            'risk_factors': self._extract_risk_factors(agent_results),
            'opportunities': self._extract_opportunities(agent_results)
        }
    
    def _get_final_recommendation_signal(self, score: float, agent_results: Dict[str, Any]) -> str:
        """Determine final recommendation signal"""
        
        # Base recommendation on score
        if score >= 0.75:
            base_signal = "STRONG_BUY"
        elif score >= 0.65:
            base_signal = "BUY"
        elif score >= 0.55:
            base_signal = "HOLD"
        elif score >= 0.45:
            base_signal = "WEAK_HOLD"
        elif score >= 0.35:
            base_signal = "SELL"
        else:
            base_signal = "STRONG_SELL"
        
        # Check for agent consensus
        agent_signals = []
        for agent_result in agent_results.values():
            if 'recommendation_signal' in agent_result:
                agent_signals.append(agent_result['recommendation_signal'])
        
        # If majority of agents strongly disagree, moderate the recommendation
        strong_negative_count = sum(1 for signal in agent_signals if signal in ['STRONG_SELL', 'SELL'])
        strong_positive_count = sum(1 for signal in agent_signals if signal in ['STRONG_BUY', 'BUY'])
        
        if len(agent_signals) >= 3:
            if strong_negative_count >= 2 and base_signal in ['STRONG_BUY', 'BUY']:
                base_signal = "HOLD"  # Moderate positive recommendation
            elif strong_positive_count >= 2 and base_signal in ['STRONG_SELL', 'SELL']:
                base_signal = "WEAK_HOLD"  # Moderate negative recommendation
        
        return base_signal
    
    def _calculate_overall_confidence(self, agent_results: Dict[str, Any], active_agents: List[str]) -> float:
        """Calculate overall confidence based on agent confidences and consensus"""
        
        confidences = []
        for agent_name in active_agents:
            if agent_name in agent_results and 'confidence' in agent_results[agent_name]:
                confidences.append(agent_results[agent_name]['confidence'])
        
        if not confidences:
            return 0.5
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences)
        
        # Adjust for consensus
        agent_signals = []
        for agent_result in agent_results.values():
            if 'recommendation_signal' in agent_result:
                agent_signals.append(agent_result['recommendation_signal'])
        
        # Calculate consensus factor
        if len(agent_signals) >= 2:
            signal_counts = {}
            for signal in agent_signals:
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
            max_count = max(signal_counts.values())
            consensus_factor = max_count / len(agent_signals)
            
            # Boost confidence if there's strong consensus
            if consensus_factor >= 0.8:  # 80%+ consensus
                avg_confidence = min(0.95, avg_confidence + 0.1)
            elif consensus_factor <= 0.4:  # Low consensus
                avg_confidence = max(0.2, avg_confidence - 0.1)
        
        return avg_confidence
    
    def _generate_summary_analysis(self, agent_results: Dict[str, Any], 
                                  final_score: float, final_signal: str) -> str:
        """Generate comprehensive summary analysis"""
        
        summary_parts = []
        
        # Overall assessment
        if final_score >= 0.7:
            summary_parts.append("Strong investment opportunity with favorable metrics across multiple dimensions.")
        elif final_score >= 0.6:
            summary_parts.append("Positive investment case with good fundamentals and technical setup.")
        elif final_score >= 0.5:
            summary_parts.append("Mixed signals suggest a balanced risk-reward profile.")
        elif final_score >= 0.4:
            summary_parts.append("Cautious outlook with several concerning factors.")
        else:
            summary_parts.append("Weak investment case with multiple risk factors.")
        
        # Agent-specific insights
        for agent_name, result in agent_results.items():
            if 'analysis' in result and result['analysis']:
                agent_display_name = agent_name.replace('_', ' ').title()
                summary_parts.append(f"{agent_display_name}: {result['analysis']}")
        
        return " ".join(summary_parts)
    
    def _extract_key_insights(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract key insights from agent analyses"""
        
        insights = []
        
        # Fundamental insights
        if 'fundamental' in agent_results:
            fund_result = agent_results['fundamental']
            if 'key_metrics' in fund_result:
                metrics = fund_result['key_metrics']
                pe_ratio = metrics.get('pe_ratio')
                roe = metrics.get('roe')
                
                if pe_ratio and pe_ratio < 15:
                    insights.append(f"Attractive valuation with P/E of {pe_ratio:.1f}")
                if roe and roe > 0.15:
                    insights.append(f"Strong profitability with ROE of {roe*100:.1f}%")
        
        # Technical insights
        if 'technical' in agent_results:
            tech_result = agent_results['technical']
            if 'key_metrics' in tech_result:
                metrics = tech_result['key_metrics']
                rsi = metrics.get('rsi14')
                
                if rsi and rsi < 30:
                    insights.append("Oversold conditions may present buying opportunity")
                elif rsi and rsi > 70:
                    insights.append("Overbought conditions suggest caution")
        
        # Risk insights
        if 'risk_assessment' in agent_results:
            risk_result = agent_results['risk_assessment']
            if 'key_metrics' in risk_result:
                metrics = risk_result['key_metrics']
                debt_equity = metrics.get('debt_to_equity')
                
                if debt_equity and debt_equity < 0.3:
                    insights.append("Conservative balance sheet with low debt")
                elif debt_equity and debt_equity > 1.0:
                    insights.append("High debt levels warrant careful monitoring")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _extract_risk_factors(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract key risk factors"""
        
        risks = []
        
        # Check each agent for risk indicators
        for agent_name, result in agent_results.items():
            if 'scores' in result:
                scores = result['scores']
                
                # Look for low scores indicating risks
                for score_name, score_value in scores.items():
                    if score_value <= 0.4:  # Low score indicates risk
                        risk_description = self._get_risk_description(agent_name, score_name, score_value)
                        if risk_description:
                            risks.append(risk_description)
        
        return risks[:4]  # Limit to top 4 risks
    
    def _extract_opportunities(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract key opportunities"""
        
        opportunities = []
        
        # Check each agent for opportunity indicators
        for agent_name, result in agent_results.items():
            if 'scores' in result:
                scores = result['scores']
                
                # Look for high scores indicating opportunities
                for score_name, score_value in scores.items():
                    if score_value >= 0.7:  # High score indicates opportunity
                        opp_description = self._get_opportunity_description(agent_name, score_name, score_value)
                        if opp_description:
                            opportunities.append(opp_description)
        
        return opportunities[:4]  # Limit to top 4 opportunities
    
    def _get_risk_description(self, agent_name: str, score_name: str, score_value: float) -> str:
        """Get human-readable risk description"""
        
        risk_map = {
            'fundamental': {
                'valuation_score': 'Expensive valuation multiples',
                'profitability_score': 'Weak profitability metrics',
                'financial_health_score': 'Poor financial health'
            },
            'technical': {
                'momentum_score': 'Negative price momentum',
                'trend_score': 'Bearish trend signals'
            },
            'risk_assessment': {
                'valuation_risk_score': 'High valuation risk',
                'financial_risk_score': 'Elevated financial risk',
                'safety_margin_score': 'Limited safety margin'
            }
        }
        
        return risk_map.get(agent_name, {}).get(score_name, '')
    
    def _get_opportunity_description(self, agent_name: str, score_name: str, score_value: float) -> str:
        """Get human-readable opportunity description"""
        
        opp_map = {
            'fundamental': {
                'valuation_score': 'Attractive valuation opportunity',
                'profitability_score': 'Strong profitability metrics',
                'growth_score': 'Solid growth prospects'
            },
            'technical': {
                'momentum_score': 'Positive momentum building',
                'trend_score': 'Strong uptrend in place'
            },
            'macro_context': {
                'gdp_impact_score': 'Favorable economic environment',
                'market_sentiment_score': 'Positive market sentiment'
            }
        }
        
        return opp_map.get(agent_name, {}).get(score_name, '')
    
    def _create_agent_error(self, agent_name: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error response for failed agent"""
        return {
            "agent_name": agent_name,
            "error": error_msg,
            "overall_score": 0.5,
            "confidence": 0.1,
            "recommendation_signal": "HOLD",
            "analysis": f"Agent {agent_name} failed: {error_msg}"
        }