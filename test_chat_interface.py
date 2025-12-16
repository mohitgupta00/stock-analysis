#!/usr/bin/env python3
"""Test the conversational chat interface"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.chat_interface import StockAnalysisChat

def test_chat_interface():
    """Test various conversational queries"""
    
    chat = StockAnalysisChat()
    
    # Test queries
    test_queries = [
        "Should I invest in INFY for long term?",
        "How is TCS performing compared to its peers?", 
        "What are the technical indicators showing for Reliance?",
        "Is HDFC Bank a good value investment?",
        "Tell me about Wipro's risks",
        "Compare Infosys with TCS",
        "What's the macro environment for IT stocks?",
        "Should I buy more INFY?",  # Follow-up query
        "Analyze some random company",  # Error case
    ]
    
    print("🤖 Testing Conversational Stock Analysis Interface")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[TEST {i}] User Query: {query}")
        print("-" * 40)
        
        try:
            response = chat.process_query(query)
            
            if 'error' in response:
                print(f"❌ Error: {response.get('error')}")
                print(f"🤖 Response: {response.get('conversational_response')}")
                
                if 'suggestions' in response:
                    print("💡 Suggestions:")
                    for suggestion in response['suggestions'][:2]:
                        print(f"  • {suggestion}")
            else:
                print(f"📈 Stock: {response.get('company', 'N/A')}")
                print(f"🎯 Recommendation: {response.get('recommendation', {}).get('signal', 'N/A')}")
                print(f"📊 Score: {response.get('recommendation', {}).get('score', 0):.3f}")
                print(f"🤖 Response: {response.get('conversational_response')}")
                
                if 'key_points' in response:
                    print("📋 Key Points:")
                    for point in response['key_points'][:3]:
                        print(f"  {point}")
                
                if 'follow_up_suggestions' in response:
                    print("💡 Follow-up suggestions:")
                    for suggestion in response['follow_up_suggestions'][:2]:
                        print(f"  • {suggestion}")
        
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Test conversation history
    print(f"\n{'='*60}")
    print("📚 CONVERSATION HISTORY")
    print(f"{'='*60}")
    
    history = chat.get_conversation_history()
    print(f"Total conversations: {len(history)}")
    
    for i, conv in enumerate(history[-3:], 1):  # Show last 3
        print(f"\n[{i}] Query: {conv['user_query']}")
        print(f"    Ticker: {conv['ticker']}")
        print(f"    Response: {conv['response']['conversational_response'][:100]}...")

if __name__ == "__main__":
    test_chat_interface()