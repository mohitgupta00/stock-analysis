# 🧠 Orchestrator Intelligence - How Agent Selection Works

## **Current System Behavior**

### **Query-Based Agent Selection**
The orchestrator uses `_determine_active_agents()` to intelligently select which agents to run based on the user's query:

```python
def _determine_active_agents(self, user_query: str) -> List[str]:
    query_lower = user_query.lower()
    
    # Default: use all agents
    active_agents = ['fundamental', 'technical', 'peer_comparison', 'macro_context', 'risk_assessment']
    
    # Query-specific agent selection
    if any(word in query_lower for word in ['fundamental', 'valuation', 'p/e', 'financial']):
        active_agents = ['fundamental', 'peer_comparison', 'risk_assessment']
        
    elif any(word in query_lower for word in ['technical', 'chart', 'trend', 'rsi']):
        active_agents = ['technical', 'risk_assessment']
        
    elif any(word in query_lower for word in ['compare', 'peer', 'vs']):
        active_agents = ['fundamental', 'peer_comparison', 'technical']
        
    elif any(word in query_lower for word in ['risk', 'safe', 'downside']):
        active_agents = ['risk_assessment', 'fundamental', 'technical']
        
    # Investment recommendation - use all agents
    elif any(word in query_lower for word in ['buy', 'sell', 'invest']):
        active_agents = ['fundamental', 'technical', 'peer_comparison', 'macro_context', 'risk_assessment']
```

## **Example Scenarios**

### **Scenario 1: Stock Comparison Query**
**User**: "Compare TCS with its peers"

**Current System**:
- **Detected Keywords**: "compare", "peers"
- **Selected Agents**: Fundamental + Peer Comparison + Technical (3 agents)
- **Reasoning**: Comparison needs fundamentals, peer data, and some technical context

**Follow-up**: "What are TCS technical indicators?"

**Current System**:
- **Detected Keywords**: "technical", "indicators"  
- **Selected Agents**: Technical + Risk Assessment (2 agents)
- **Context**: Loses previous comparison context, treats as new query

### **Scenario 2: Investment Decision Query**
**User**: "Should I invest in INFY?"

**Current System**:
- **Detected Keywords**: "invest"
- **Selected Agents**: All 5 agents
- **Reasoning**: Investment decisions need comprehensive analysis

**Follow-up**: "What about the risks?"

**Current System**:
- **Detected Keywords**: "risks"
- **Selected Agents**: Risk + Fundamental + Technical (3 agents)
- **Context**: Uses previous ticker (INFY) but different agent set

## **IDEAL vs CURRENT System**

### **IDEAL Behavior**
```
User: "Compare INFY with TCS"
System: Runs Fundamental + Peer + Technical agents for both stocks
Context: Stores comparison results for INFY vs TCS

User: "Show me INFY's technical indicators"
System: 
- Recognizes INFY from previous context
- Runs ONLY Technical agent (efficient)
- References previous comparison for context
- Response: "From our earlier comparison, INFY's technical indicators show..."
```

### **CURRENT Behavior**
```
User: "Compare INFY with TCS"  
System: Extracts "INFY" as ticker, runs 3 agents for INFY only
Context: Stores INFY analysis

User: "Show me INFY's technical indicators"
System:
- Recognizes INFY from context ✓
- Runs Technical + Risk agents (2 agents)
- No reference to previous comparison ✗
- Response: Fresh technical analysis without comparison context
```

## **Key Differences**

### **Context Continuity**
- **IDEAL**: "Based on our earlier comparison with TCS, INFY's RSI of 62 is higher than TCS's 58..."
- **CURRENT**: "INFY's RSI is 62, indicating neutral momentum..." (no comparison context)

### **Agent Efficiency**
- **IDEAL**: Single Technical agent for follow-up technical query
- **CURRENT**: Technical + Risk agents (always includes Risk for safety)

### **Multi-Stock Handling**
- **IDEAL**: "Compare A with B" analyzes both stocks
- **CURRENT**: "Compare A with B" only analyzes stock A

## **System Strengths**

### **✅ What Works Well**
1. **Smart Agent Selection**: Correctly identifies query intent
2. **Context Awareness**: Remembers previous ticker for follow-ups
3. **Safety First**: Always includes Risk agent when relevant
4. **Keyword Detection**: Accurately maps queries to agent types

### **Example of Good Behavior**
```
Query: "What are the technical indicators for Reliance?"
✓ Correctly extracts "RELIANCE.NS"
✓ Selects Technical + Risk agents (appropriate)
✓ Provides focused technical analysis
✓ Includes risk context for safety
```

## **Areas for Improvement**

### **🔄 Context Enhancement Needed**
1. **Conversation Memory**: Link follow-up responses to previous analysis
2. **Multi-Stock Queries**: Handle "Compare A with B" properly
3. **Progressive Disclosure**: Build on previous insights
4. **Cross-Agent References**: "As mentioned in fundamental analysis..."

### **🎯 Efficiency Optimizations**
1. **Single Agent Follow-ups**: Pure technical queries shouldn't need Risk agent
2. **Cached Results**: Reuse previous agent results when appropriate
3. **Incremental Analysis**: Update only changed aspects

## **Real Example from Test**

### **Query**: "Compare TCS fundamentals with peers"
**Current Output**:
```
🤖 ACTIVE AGENTS: fundamental, peer_comparison, risk_assessment

📝 SUMMARY: 
Fundamental: P/E: 23.45, ROE: 47.4%, D/E: 10.17...
Peer Comparison: Trading at 11.0% discount to peer median P/E...
Risk Assessment: High valuation risk - trading at expensive multiples...
```

**Ideal Enhancement**:
```
🤖 ACTIVE AGENTS: fundamental, peer_comparison

📝 SUMMARY:
TCS shows superior fundamentals vs peers:
- ROE 94.7% above peer median (47.4% vs 24.3%)
- Trading at 11% discount despite outperformance
- Ranks #1 in profitability among IT peers
- Risk: High debt levels need monitoring
```

## **Conclusion**

**Current System**: ✅ **Functional and Smart**
- Correctly selects relevant agents
- Handles context for ticker continuity
- Provides comprehensive analysis

**Enhancement Opportunity**: 🚀 **Context Continuity**
- Better conversation flow
- Multi-stock comparison handling
- Progressive insight building
- More natural follow-up responses

The system works well for individual queries but could be enhanced for conversational continuity and multi-stock scenarios.