#!/usr/bin/env python3
"""Conversational interface for stock analysis"""

import sys
import os
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import MultiAgentOrchestrator

class StockAnalysisChat:
    """Conversational interface for multi-agent stock analysis"""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.conversation_history = []
        self.context = {}
        
        # Common NSE ticker mappings
        self.ticker_mappings = {
            'infosys': 'INFY.NS',
            'infy': 'INFY.NS',
            'tcs': 'TCS.NS',
            'tata consultancy': 'TCS.NS',
            'reliance': 'RELIANCE.NS',
            'ril': 'RELIANCE.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'hdfcbank': 'HDFCBANK.NS',
            'icici bank': 'ICICIBANK.NS',
            'icicibank': 'ICICIBANK.NS',
            'wipro': 'WIPRO.NS',
            'hcl tech': 'HCLTECH.NS',
            'hcltech': 'HCLTECH.NS',
            'tech mahindra': 'TECHM.NS',
            'techm': 'TECHM.NS',
            'itc': 'ITC.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'hul': 'HINDUNILVR.NS',
            'maruti': 'MARUTI.NS',
            'tata motors': 'TATAMOTORS.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'axis bank': 'AXISBANK.NS',
            'kotak bank': 'KOTAKBANK.NS',
            'sbi': 'SBIN.NS',
            'larsen toubro': 'LT.NS',
            'lt': 'LT.NS'
        }
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process user query and return analysis"""
        
        # Extract ticker and preference from query
        ticker = self._extract_ticker(user_input)
        preference = self._extract_preference(user_input)
        
        if not ticker:
            return self._create_help_response(user_input)
        
        # Update context
        self.context.update({
            'last_ticker': ticker,
            'last_preference': preference,
            'last_query': user_input
        })
        
        try:
            # Run multi-agent analysis
            result = self.orchestrator.analyze_stock(
                ticker=ticker,
                user_query=user_input,
                user_preference=preference
            )
            
            # Format response for conversation
            response = self._format_conversational_response(result, user_input)
            
            # Add to conversation history
            self.conversation_history.append({
                'user_query': user_input,
                'ticker': ticker,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _extract_ticker(self, query: str) -> Optional[str]:
        """Extract stock ticker from user query"""
        
        query_lower = query.lower()
        
        # Check for company name mappings first (more reliable)
        for company_name, ticker in self.ticker_mappings.items():
            if company_name in query_lower:
                return ticker
        
        # Check for direct ticker mentions (e.g., "INFY.NS", "TCS")
        ticker_pattern = r'\b([A-Z]{2,10}(?:\.NS)?)\b'
        ticker_matches = re.findall(ticker_pattern, query.upper())
        
        if ticker_matches:
            ticker = ticker_matches[0]
            if not ticker.endswith('.NS'):
                ticker += '.NS'
            # Verify it's a known ticker
            if ticker in self.ticker_mappings.values():
                return ticker
        
        # Check context for previous ticker
        if 'last_ticker' in self.context:
            # If query doesn't mention a new stock, use previous one
            follow_up_indicators = ['it', 'this stock', 'the stock', 'same', 'also', 'more']
            if any(indicator in query_lower for indicator in follow_up_indicators):
                return self.context['last_ticker']
        
        return None
    
    def _extract_preference(self, query: str) -> str:
        """Extract investment preference from query"""
        
        query_lower = query.lower()
        
        # Value investing indicators
        value_keywords = ['value', 'cheap', 'undervalued', 'bargain', 'discount', 'pe ratio', 'book value']
        if any(keyword in query_lower for keyword in value_keywords):
            return 'value'
        
        # Growth investing indicators  
        growth_keywords = ['growth', 'momentum', 'trending', 'rising', 'expanding', 'revenue growth']
        if any(keyword in query_lower for keyword in growth_keywords):
            return 'growth'
        
        # Use context or default to balanced
        return self.context.get('last_preference', 'balanced')
    
    def _format_conversational_response(self, analysis_result: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Format analysis result for conversational interface"""
        
        ticker = analysis_result.get('ticker', '')
        company_name = ticker.replace('.NS', '')
        recommendation = analysis_result.get('recommendation', {})
        
        # Create conversational response
        response = {
            'ticker': ticker,
            'company': company_name,
            'recommendation': recommendation,
            'conversational_response': self._generate_conversational_text(analysis_result, user_query),
            'key_points': self._extract_key_points(analysis_result),
            'detailed_analysis': analysis_result.get('summary_analysis', ''),
            'agent_insights': self._format_agent_insights(analysis_result),
            'follow_up_suggestions': self._generate_follow_up_suggestions(analysis_result),
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def _generate_conversational_text(self, analysis_result: Dict[str, Any], user_query: str) -> str:
        """Generate natural conversational response"""
        
        ticker = analysis_result.get('ticker', '').replace('.NS', '')
        recommendation = analysis_result.get('recommendation', {})
        signal = recommendation.get('signal', 'HOLD')
        score = recommendation.get('score', 0.5)
        confidence = recommendation.get('confidence', 0.5)
        
        # Opening based on recommendation
        if signal in ['STRONG_BUY', 'BUY']:
            opening = f"Based on my analysis, {ticker} looks like a good investment opportunity."
        elif signal in ['STRONG_SELL', 'SELL']:
            opening = f"I'd be cautious about {ticker} right now."
        else:
            opening = f"{ticker} presents a mixed investment picture."
        
        # Score interpretation
        score_text = ""
        if score >= 0.7:
            score_text = f"With a strong score of {score:.2f}, the fundamentals and technicals align well."
        elif score >= 0.6:
            score_text = f"The analysis score of {score:.2f} suggests decent potential."
        elif score >= 0.5:
            score_text = f"The score of {score:.2f} indicates balanced risk-reward."
        else:
            score_text = f"The lower score of {score:.2f} suggests some concerns."
        
        # Confidence level
        confidence_text = ""
        if confidence >= 0.8:
            confidence_text = f"I'm quite confident in this assessment ({confidence:.0%} confidence)."
        elif confidence >= 0.6:
            confidence_text = f"I have moderate confidence in this analysis ({confidence:.0%})."
        else:
            confidence_text = f"This analysis has limited confidence ({confidence:.0%}) due to data constraints."
        
        # Key insights
        insights = analysis_result.get('key_insights', [])
        insight_text = ""
        if insights:
            insight_text = f" Key highlights: {insights[0]}"
            if len(insights) > 1:
                insight_text += f" and {insights[1]}"
        
        return f"{opening} {score_text} {confidence_text}{insight_text}"
    
    def _extract_key_points(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract key points for bullet format"""
        
        points = []
        
        # Recommendation
        recommendation = analysis_result.get('recommendation', {})
        signal = recommendation.get('signal', 'HOLD')
        score = recommendation.get('score', 0.5)
        
        points.append(f"Recommendation: {signal} (Score: {score:.2f})")
        
        # Top insights
        insights = analysis_result.get('key_insights', [])
        for insight in insights[:2]:
            points.append(f"✓ {insight}")
        
        # Top risk
        risks = analysis_result.get('risk_factors', [])
        if risks:
            points.append(f"⚠ {risks[0]}")
        
        # Top opportunity
        opportunities = analysis_result.get('opportunities', [])
        if opportunities:
            points.append(f"🚀 {opportunities[0]}")
        
        return points
    
    def _format_agent_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Format insights from each agent"""
        
        agent_insights = {}
        agent_results = analysis_result.get('agent_results', {})
        
        for agent_name, result in agent_results.items():
            if 'analysis' in result:
                agent_display_name = agent_name.replace('_', ' ').title()
                agent_insights[agent_display_name] = result['analysis']
        
        return agent_insights
    
    def _generate_follow_up_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate follow-up question suggestions"""
        
        suggestions = []
        ticker = analysis_result.get('ticker', '').replace('.NS', '')
        
        # Based on recommendation
        recommendation = analysis_result.get('recommendation', {})
        signal = recommendation.get('signal', 'HOLD')
        
        if signal in ['BUY', 'STRONG_BUY']:
            suggestions.extend([
                f"What are the main risks with {ticker}?",
                f"How does {ticker} compare to its peers?",
                f"What's the best entry price for {ticker}?"
            ])
        elif signal in ['SELL', 'STRONG_SELL']:
            suggestions.extend([
                f"Why is {ticker} performing poorly?",
                f"Are there better alternatives to {ticker}?",
                f"What would make {ticker} a buy again?"
            ])
        else:
            suggestions.extend([
                f"What are {ticker}'s growth prospects?",
                f"Show me {ticker}'s technical analysis",
                f"What's the macro environment for {ticker}?"
            ])
        
        # Generic suggestions
        suggestions.extend([
            f"Compare {ticker} with TCS",
            f"What's {ticker}'s dividend yield?",
            "Analyze RELIANCE for value investing"
        ])
        
        return suggestions[:4]
    
    def _create_help_response(self, user_input: str) -> Dict[str, Any]:
        """Create help response when ticker not found"""
        
        return {
            'error': 'ticker_not_found',
            'conversational_response': "I couldn't identify which stock you're asking about. Please mention a company name or ticker symbol like 'INFY', 'TCS', or 'Reliance'.",
            'suggestions': [
                "Should I invest in INFY?",
                "Analyze TCS for value investing",
                "Compare RELIANCE with its peers",
                "What are the technical indicators for HDFCBANK?",
                "Show me WIPRO's fundamental analysis"
            ],
            'available_stocks': list(self.ticker_mappings.keys())[:10],
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        
        return {
            'error': 'analysis_failed',
            'conversational_response': f"I encountered an issue while analyzing the stock: {error_msg}. Please try again or ask about a different stock.",
            'suggestions': [
                "Try asking about a popular stock like INFY or TCS",
                "Check if the company name is spelled correctly",
                "Ask for help with available stocks"
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context = {}

# CLI Interface for testing
def main():
    """Command line interface for testing"""
    
    chat = StockAnalysisChat()
    
    print("🤖 Stock Analysis AI Assistant")
    print("Ask me about any NSE stock! Type 'quit' to exit, 'help' for examples.")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Happy investing!")
                break
            
            if user_input.lower() == 'help':
                print("\n📚 Example queries:")
                print("  • Should I invest in INFY?")
                print("  • Analyze TCS for value investing")
                print("  • Compare RELIANCE with peers")
                print("  • What are HDFCBANK's technical indicators?")
                print("  • Show me WIPRO's risks")
                continue
            
            if not user_input:
                continue
            
            print("\n🔍 Analyzing...")
            
            response = chat.process_query(user_input)
            
            if 'error' in response:
                print(f"\n🤖 Assistant: {response['conversational_response']}")
                if 'suggestions' in response:
                    print("\n💡 Try asking:")
                    for suggestion in response['suggestions'][:3]:
                        print(f"  • {suggestion}")
            else:
                print(f"\n🤖 Assistant: {response['conversational_response']}")
                
                if 'key_points' in response:
                    print(f"\n📊 Key Points:")
                    for point in response['key_points']:
                        print(f"  {point}")
                
                if 'follow_up_suggestions' in response:
                    print(f"\n💡 You might also ask:")
                    for suggestion in response['follow_up_suggestions'][:2]:
                        print(f"  • {suggestion}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Happy investing!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()