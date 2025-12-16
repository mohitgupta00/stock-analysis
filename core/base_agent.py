from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all analysis agents"""
    
    def __init__(self, name: str, weight: float):
        self.name = name
        self.weight = weight
        self.last_analysis = None
        
    @abstractmethod
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform agent-specific analysis"""
        pass
    
    def get_recommendation_signal(self, score: float) -> str:
        """Convert score to recommendation signal"""
        if score >= 0.75:
            return "STRONG_BUY"
        elif score >= 0.65:
            return "BUY"
        elif score >= 0.55:
            return "HOLD"
        elif score >= 0.45:
            return "WEAK_HOLD"
        elif score >= 0.35:
            return "SELL"
        else:
            return "STRONG_SELL"
    
    def create_response(self, scores: Dict[str, float], analysis: str, 
                       key_metrics: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Create standardized agent response"""
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "scores": scores,
            "overall_score": overall_score,
            "analysis": analysis,
            "key_metrics": key_metrics,
            "recommendation_signal": self.get_recommendation_signal(overall_score),
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }