import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_agent import BaseAgent
from data.pricefetcher import PriceFetcher
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

class PeerComparisonAgent(BaseAgent):
    """Agent for peer comparison analysis within sector"""
    
    def __init__(self):
        super().__init__("Peer_Comparison_Agent", weight=0.15)
        self.fetcher = PriceFetcher()
        
        # Predefined sector peers for major stocks
        self.sector_peers = {
            'INFY.NS': ['TCS.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
            'TCS.NS': ['INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
            'RELIANCE.NS': ['ONGC.NS', 'IOC.NS', 'BPCL.NS'],
            'HDFCBANK.NS': ['ICICIBANK.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS'],
            'ICICIBANK.NS': ['HDFCBANK.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS'],
            'ITC.NS': ['HUL.NS', 'NESTLEIND.NS', 'BRITANNIA.NS'],
            'HINDUNILVR.NS': ['ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS'],
            'MARUTI.NS': ['TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS'],
            'TATAMOTORS.NS': ['MARUTI.NS', 'M&M.NS', 'BAJAJ-AUTO.NS']
        }
        
    def analyze(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform peer comparison analysis"""
        try:
            # Get target stock fundamentals
            target_fundamentals = self.fetcher.fetch_fundamentals(ticker)
            
            if "error" in target_fundamentals:
                return self._create_error_response(f"Cannot fetch target stock data: {target_fundamentals['error']}")
            
            # Get peer stocks
            peers = self._get_peers(ticker, target_fundamentals.get('sector'))
            
            if not peers:
                return self._create_limited_analysis(target_fundamentals, "No peer data available")
            
            # Fetch peer data
            peer_data = self._fetch_peer_data(peers)
            
            # Calculate relative scores
            scores = self._calculate_peer_scores(target_fundamentals, peer_data)
            
            # Generate analysis
            analysis = self._generate_analysis(ticker, target_fundamentals, peer_data, scores)
            
            return self.create_response(
                scores=scores,
                analysis=analysis,
                key_metrics=self._extract_key_metrics(target_fundamentals, peer_data),
                confidence=self._calculate_confidence(peer_data)
            )
            
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _get_peers(self, ticker: str, sector: str) -> List[str]:
        """Get peer stocks for comparison"""
        # First try predefined peers
        if ticker in self.sector_peers:
            return self.sector_peers[ticker]
        
        # Fallback: try to find peers from NSE data based on sector
        try:
            clean_file = '/home/sagemaker-user/stock-analysis/data/nse_stocks_clean.csv'
            if os.path.exists(clean_file):
                df = pd.read_csv(clean_file)
                # For now, return some Group A stocks as generic peers
                group_a_stocks = df[df['group'] == 'A']['security_id'].head(5).tolist()
                return [f"{stock}.NS" for stock in group_a_stocks if f"{stock}.NS" != ticker]
        except:
            pass
        
        return []
    
    def _fetch_peer_data(self, peers: List[str]) -> List[Dict[str, Any]]:
        """Fetch fundamental data for peer stocks"""
        peer_data = []
        
        for peer_ticker in peers[:4]:  # Limit to 4 peers to avoid rate limits
            try:
                peer_fundamentals = self.fetcher.fetch_fundamentals(peer_ticker)
                if "error" not in peer_fundamentals:
                    peer_fundamentals['ticker'] = peer_ticker
                    peer_data.append(peer_fundamentals)
            except:
                continue
        
        return peer_data
    
    def _calculate_peer_scores(self, target: Dict[str, Any], peers: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate scores based on peer comparison"""
        scores = {}
        
        if not peers:
            return {'relative_valuation_score': 0.5, 'relative_profitability_score': 0.5, 'peer_ranking_score': 0.5}
        
        # Relative Valuation Score (P/E comparison)
        target_pe = target.get('pe_ratio')
        peer_pes = [p.get('pe_ratio') for p in peers if p.get('pe_ratio')]
        
        valuation_score = 0.5
        if target_pe and peer_pes:
            peer_median_pe = sorted(peer_pes)[len(peer_pes)//2]
            
            if target_pe < peer_median_pe * 0.8:  # 20% cheaper than peers
                valuation_score = 0.8
            elif target_pe < peer_median_pe:  # Cheaper than median
                valuation_score = 0.7
            elif target_pe > peer_median_pe * 1.2:  # 20% more expensive
                valuation_score = 0.3
            elif target_pe > peer_median_pe:  # More expensive than median
                valuation_score = 0.4
        
        scores['relative_valuation_score'] = valuation_score
        
        # Relative Profitability Score (ROE comparison)
        target_roe = target.get('roe')
        peer_roes = [p.get('roe') for p in peers if p.get('roe')]
        
        profitability_score = 0.5
        if target_roe and peer_roes:
            peer_median_roe = sorted(peer_roes)[len(peer_roes)//2]
            
            if target_roe > peer_median_roe * 1.2:  # 20% better ROE
                profitability_score = 0.8
            elif target_roe > peer_median_roe:  # Better than median
                profitability_score = 0.7
            elif target_roe < peer_median_roe * 0.8:  # 20% worse ROE
                profitability_score = 0.3
            elif target_roe < peer_median_roe:  # Worse than median
                profitability_score = 0.4
        
        scores['relative_profitability_score'] = profitability_score
        
        # Overall Peer Ranking Score
        ranking_factors = []
        
        # P/E ranking (lower is better)
        if target_pe and peer_pes:
            all_pes = peer_pes + [target_pe]
            pe_rank = sorted(all_pes).index(target_pe) + 1
            pe_percentile = (len(all_pes) - pe_rank + 1) / len(all_pes)
            ranking_factors.append(pe_percentile)
        
        # ROE ranking (higher is better)
        if target_roe and peer_roes:
            all_roes = peer_roes + [target_roe]
            roe_rank = sorted(all_roes, reverse=True).index(target_roe) + 1
            roe_percentile = (len(all_roes) - roe_rank + 1) / len(all_roes)
            ranking_factors.append(roe_percentile)
        
        if ranking_factors:
            scores['peer_ranking_score'] = sum(ranking_factors) / len(ranking_factors)
        else:
            scores['peer_ranking_score'] = 0.5
        
        return scores
    
    def _generate_analysis(self, ticker: str, target: Dict[str, Any], 
                          peers: List[Dict[str, Any]], scores: Dict[str, float]) -> str:
        """Generate peer comparison analysis"""
        
        if not peers:
            return "Limited peer comparison data available."
        
        target_pe = target.get('pe_ratio')
        target_roe = target.get('roe')
        
        analysis_parts = []
        
        # P/E comparison
        if target_pe:
            peer_pes = [p.get('pe_ratio') for p in peers if p.get('pe_ratio')]
            if peer_pes:
                peer_median_pe = sorted(peer_pes)[len(peer_pes)//2]
                pe_diff = ((target_pe - peer_median_pe) / peer_median_pe) * 100
                
                if pe_diff < -10:
                    analysis_parts.append(f"Trading at {abs(pe_diff):.1f}% discount to peer median P/E.")
                elif pe_diff > 10:
                    analysis_parts.append(f"Trading at {pe_diff:.1f}% premium to peer median P/E.")
                else:
                    analysis_parts.append("P/E in line with peer group.")
        
        # ROE comparison
        if target_roe:
            peer_roes = [p.get('roe') for p in peers if p.get('roe')]
            if peer_roes:
                peer_median_roe = sorted(peer_roes)[len(peer_roes)//2]
                roe_diff = ((target_roe - peer_median_roe) / peer_median_roe) * 100
                
                if roe_diff > 10:
                    analysis_parts.append(f"ROE {roe_diff:.1f}% above peer median - superior profitability.")
                elif roe_diff < -10:
                    analysis_parts.append(f"ROE {abs(roe_diff):.1f}% below peer median - underperforming.")
                else:
                    analysis_parts.append("ROE comparable to peers.")
        
        # Overall ranking
        ranking_score = scores.get('peer_ranking_score', 0.5)
        if ranking_score >= 0.7:
            analysis_parts.append("Ranks in top tier among peers.")
        elif ranking_score <= 0.3:
            analysis_parts.append("Ranks in bottom tier among peers.")
        else:
            analysis_parts.append("Middle-tier ranking among peers.")
        
        peer_tickers = [p.get('ticker', '').replace('.NS', '') for p in peers]
        analysis_parts.append(f"Compared against: {', '.join(peer_tickers[:3])}.")
        
        return " ".join(analysis_parts)
    
    def _extract_key_metrics(self, target: Dict[str, Any], peers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract key peer comparison metrics"""
        
        metrics = {
            'target_pe': target.get('pe_ratio'),
            'target_roe': target.get('roe'),
            'target_market_cap': target.get('market_cap'),
            'peer_count': len(peers)
        }
        
        if peers:
            peer_pes = [p.get('pe_ratio') for p in peers if p.get('pe_ratio')]
            peer_roes = [p.get('roe') for p in peers if p.get('roe')]
            
            if peer_pes:
                metrics['peer_median_pe'] = sorted(peer_pes)[len(peer_pes)//2]
                metrics['peer_avg_pe'] = sum(peer_pes) / len(peer_pes)
            
            if peer_roes:
                metrics['peer_median_roe'] = sorted(peer_roes)[len(peer_roes)//2]
                metrics['peer_avg_roe'] = sum(peer_roes) / len(peer_roes)
            
            metrics['peer_tickers'] = [p.get('ticker') for p in peers]
        
        return metrics
    
    def _calculate_confidence(self, peers: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on peer data availability"""
        if not peers:
            return 0.2
        
        # Higher confidence with more peers and better data quality
        peer_count_factor = min(1.0, len(peers) / 3)  # Optimal is 3+ peers
        
        # Check data quality
        complete_peers = sum(1 for p in peers if p.get('pe_ratio') and p.get('roe'))
        data_quality_factor = complete_peers / len(peers) if peers else 0
        
        return min(0.9, 0.4 + peer_count_factor * 0.3 + data_quality_factor * 0.2)
    
    def _create_limited_analysis(self, target: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Create limited analysis when peer data is unavailable"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "scores": {
                'relative_valuation_score': 0.5,
                'relative_profitability_score': 0.5,
                'peer_ranking_score': 0.5
            },
            "overall_score": 0.5,
            "analysis": f"Peer comparison limited: {reason}. Target P/E: {target.get('pe_ratio', 'N/A')}, ROE: {target.get('roe', 'N/A')}.",
            "key_metrics": {
                'target_pe': target.get('pe_ratio'),
                'target_roe': target.get('roe'),
                'peer_count': 0
            },
            "recommendation_signal": "HOLD",
            "confidence": 0.3,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "agent_name": self.name,
            "weight": self.weight,
            "error": error_msg,
            "scores": {},
            "overall_score": 0.5,
            "analysis": f"Unable to perform peer comparison: {error_msg}",
            "key_metrics": {},
            "recommendation_signal": "HOLD",
            "confidence": 0.1,
            "timestamp": datetime.now().isoformat()
        }