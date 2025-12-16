#!/usr/bin/env python3
"""Test the multi-agent analysis system"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.orchestrator import MultiAgentOrchestrator
from datetime import datetime

def test_multi_agent_analysis():
    """Test multi-agent analysis with different queries"""
    
    orchestrator = MultiAgentOrchestrator()
    
    # Test cases with different query types
    test_cases = [
        {
            'ticker': 'INFY.NS',
            'query': 'Should I invest in INFY for long term?',
            'preference': 'balanced'
        },
        {
            'ticker': 'TCS.NS', 
            'query': 'Compare TCS fundamentals with peers',
            'preference': 'value'
        },
        {
            'ticker': 'RELIANCE.NS',
            'query': 'What are the technical indicators showing?',
            'preference': 'growth'
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}: {test_case['ticker']}")
        print(f"Query: {test_case['query']}")
        print(f"Preference: {test_case['preference']}")
        print(f"{'='*60}")
        
        try:
            # Run multi-agent analysis
            result = orchestrator.analyze_stock(
                ticker=test_case['ticker'],
                user_query=test_case['query'],
                user_preference=test_case['preference']
            )
            
            # Display results
            print(f"\n🎯 FINAL RECOMMENDATION")
            print(f"Signal: {result['recommendation']['signal']}")
            print(f"Score: {result['recommendation']['score']:.3f}")
            print(f"Confidence: {result['recommendation']['confidence']:.3f}")
            
            print(f"\n📊 AGENT SCORES")
            for agent, score in result['agent_scores'].items():
                print(f"  {agent.replace('_', ' ').title()}: {score:.3f}")
            
            print(f"\n📝 SUMMARY ANALYSIS")
            print(f"{result['summary_analysis']}")
            
            if result['key_insights']:
                print(f"\n💡 KEY INSIGHTS")
                for insight in result['key_insights']:
                    print(f"  • {insight}")
            
            if result['risk_factors']:
                print(f"\n⚠️ RISK FACTORS")
                for risk in result['risk_factors']:
                    print(f"  • {risk}")
            
            if result['opportunities']:
                print(f"\n🚀 OPPORTUNITIES")
                for opp in result['opportunities']:
                    print(f"  • {opp}")
            
            print(f"\n🤖 ACTIVE AGENTS: {', '.join(result['active_agents'])}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"multi_agent_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"✅ Multi-agent testing completed!")
    print(f"📁 Detailed results saved to: {filename}")
    print(f"🧪 Test cases completed: {len(results)}/{len(test_cases)}")
    
    return results

def test_individual_agents():
    """Test individual agents separately"""
    
    print(f"\n{'='*60}")
    print("TESTING INDIVIDUAL AGENTS")
    print(f"{'='*60}")
    
    from agents.fundamental_agent import FundamentalAnalysisAgent
    from agents.technical_agent import TechnicalAnalysisAgent
    from agents.peer_comparison_agent import PeerComparisonAgent
    from agents.macro_context_agent import MacroContextAgent
    from agents.risk_assessment_agent import RiskAssessmentAgent
    
    agents = {
        'Fundamental': FundamentalAnalysisAgent(),
        'Technical': TechnicalAnalysisAgent(),
        'Peer Comparison': PeerComparisonAgent(),
        'Macro Context': MacroContextAgent(),
        'Risk Assessment': RiskAssessmentAgent()
    }
    
    ticker = 'INFY.NS'
    context = {'user_preference': 'balanced'}
    
    for agent_name, agent in agents.items():
        print(f"\n--- {agent_name} Agent ---")
        try:
            result = agent.analyze(ticker, context)
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Score: {result['overall_score']:.3f}")
                print(f"📊 Signal: {result['recommendation_signal']}")
                print(f"🎯 Confidence: {result['confidence']:.3f}")
                print(f"📝 Analysis: {result['analysis']}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Stock Analysis System Test")
    
    # Test individual agents first
    test_individual_agents()
    
    # Test full multi-agent system
    test_multi_agent_analysis()
    
    print(f"\n🎉 All tests completed!")