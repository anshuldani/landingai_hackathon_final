"""
Production Orchestrator for Activist Intel Agent
Coordinates SEC fetching, document extraction, and multi-agent analysis
OpenAI-powered version
"""

import asyncio
from typing import Dict
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ActivistIntelOrchestrator:
    """Main controller that coordinates all agents and tools"""
    
    def __init__(self):
        # Load API keys from environment
        # LandingAI SDK uses VISION_AGENT_API_KEY by default, but we support both names
        self.landing_ai_key = os.getenv('VISION_AGENT_API_KEY') or os.getenv('LANDING_AI_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Check which analysis LLM to use
        self.llm_key = self.openai_key or self.anthropic_key
        
        if not self.landing_ai_key:
            print("\n⚠️  WARNING: LandingAI API key not found in environment!")
            print("Set VISION_AGENT_API_KEY or LANDING_AI_API_KEY in .env file.")
            print("LandingAI SDK requires this for document extraction.\n")
        
        if not self.llm_key:
            print("\n⚠️  WARNING: No analysis LLM API key found!")
            print("Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env for AI analysis.")
            print("Using rule-based analysis instead.\n")
        
        # Import tools
        from tools.sec_fetcher import SECFetcher
        from tools.ade_extractor import LandingAISDKExtractor
        from tools.ratio_calculator import RatioCalculator
        from tools.peer_comparator import PeerComparator
        from tools.market_data import MarketDataFetcher
        
        # Import agents
        from agents.analyst_agent import FinancialAnalystAgent
        from agents.governance_agent import GovernanceAnalystAgent
        from agents.thesis_generator import ThesisGeneratorAgent
        
        # Initialize tools
        self.sec_fetcher_class = SECFetcher
        self.ade_extractor = LandingAISDKExtractor(self.landing_ai_key)
        self.ratio_calculator = RatioCalculator()
        self.peer_comparator = PeerComparator()
        self.market_fetcher = MarketDataFetcher()
        
        # Initialize agents (with whichever LLM key is available)
        self.financial_agent = FinancialAnalystAgent(self.llm_key) if self.llm_key else None
        self.governance_agent = GovernanceAnalystAgent(self.llm_key) if self.llm_key else None
        self.thesis_agent = ThesisGeneratorAgent(self.llm_key) if self.llm_key else None
    
    async def analyze_company(self, ticker: str) -> Dict:
        """
        Complete end-to-end analysis pipeline with REAL DATA
        
        Returns analysis results dictionary
        """
        
        start_time = time.time()
        
        # STAGE 1: Fetch real SEC filings
        print(f"\n{'='*70}")
        print(f"STAGE 1: SEC EDGAR FILING RETRIEVAL")
        print(f"{'='*70}")
        
        try:
            fetcher = self.sec_fetcher_class(ticker)
            filings = fetcher.fetch_filings(['10-K', 'DEF 14A', '8-K'], years=3)
        except Exception as e:
            print(f"  ⚠️ Error fetching SEC filings: {str(e)}")
            raise Exception(f"Failed to fetch SEC filings for {ticker}. Please verify the ticker symbol is correct.")
        
        # STAGE 2: Extract data with LandingAI Direct API
        print(f"\n{'='*70}")
        print(f"STAGE 2: LANDINGAI DIRECT API DOCUMENT EXTRACTION")
        print(f"{'='*70}")
        
        extracted_data = await self.ade_extractor.process_all_documents(filings)
        
        # STAGE 3: Fetch real-time market data
        print(f"\n{'='*70}")
        print(f"STAGE 3: MARKET DATA RETRIEVAL")
        print(f"{'='*70}")
        
        try:
            market_data = self.market_fetcher.get_market_data(ticker)
            extracted_data['market_data'] = market_data
        except Exception as e:
            print(f"  ⚠️ Warning: Market data retrieval failed: {str(e)}")
            print(f"  ℹ️ Continuing with estimated market data")
            extracted_data['market_data'] = {
                'market_cap': 0,
                'current_price': 0,
                'shares_outstanding': 0,
                'enterprise_value': 0,
                'beta': 1.0,
                'trailing_pe': 0,
                'forward_pe': 0,
                'price_to_book': 0,
                'dividend_yield': 0,
                'fifty_two_week_high': 0,
                'fifty_two_week_low': 0
            }
        
        # STAGE 4: Calculate financial metrics
        print(f"\n{'='*70}")
        print(f"STAGE 4: FINANCIAL ANALYSIS")
        print(f"{'='*70}")
        
        print(f"  📊 Calculating financial ratios...")
        metrics = self.ratio_calculator.calculate_all_ratios(extracted_data)
        red_flags = self.ratio_calculator.get_activist_red_flags(metrics)
        
        print(f"    ✅ ROE: {metrics.roe:.1f}%")
        print(f"    ✅ ROIC: {metrics.roic:.1f}%")
        print(f"    ✅ Operating Margin: {metrics.operating_margin:.1f}%")
        
        # STAGE 5: Peer comparison
        print(f"\n{'='*70}")
        print(f"STAGE 5: PEER GROUP BENCHMARKING")
        print(f"{'='*70}")
        
        print(f"  🔍 Comparing to industry peers...")
        peer_comparison = self.peer_comparator.compare_to_peers(
            ticker, 
            {
                'roe': metrics.roe,
                'roic': metrics.roic,
                'operating_margin': metrics.operating_margin,
                'revenue_current': extracted_data['10k']['revenue_current'],
                'market_cap': market_data['market_cap'],
                'enterprise_value': metrics.enterprise_value,
                'total_debt': extracted_data['10k'].get('total_debt', 0),
                'cash_equivalents': extracted_data['10k'].get('cash_equivalents', 0)
            }
        )
        
        print(f"    ✅ Peer analysis complete")
        
        # STAGE 6: Generate basic thesis
        print(f"\n{'='*70}")
        print(f"STAGE 6: INVESTMENT THESIS GENERATION")
        print(f"{'='*70}")
        
        print(f"  📝 Synthesizing basic investment thesis...")
        basic_thesis = self._generate_basic_thesis(ticker, fetcher.company_name, metrics, red_flags, peer_comparison, extracted_data)
        
        # STAGE 7: AI Agent Analysis (if LLM available)
        print(f"\n{'='*70}")
        print(f"STAGE 7: AI AGENT ANALYSIS")
        print(f"{'='*70}")
        
        if self.llm_key and self.financial_agent:
            try:
                # Financial analysis
                financial_analysis = self.financial_agent.analyze(extracted_data)
                
                # Governance analysis
                governance_analysis = self.governance_agent.analyze(extracted_data)
                
                # Generate AI thesis
                print(f"  📝 Generating comprehensive AI investment thesis...")
                ai_thesis = self.thesis_agent.generate_thesis(
                    financial_analysis,
                    governance_analysis,
                    fetcher.company_name,
                    ticker,
                    extracted_data
                )
            except Exception as e:
                error_msg = str(e)
                if 'insufficient_quota' in error_msg or '429' in error_msg:
                    print(f"  ⚠️  OpenAI API quota exceeded - using rule-based analysis")
                    print(f"  💡 Add credits to your OpenAI account or remove OPENAI_API_KEY from .env")
                else:
                    print(f"  ⚠️  AI analysis error: {error_msg}")
                
                # Fall back to rule-based
                financial_analysis = "Rule-based analysis (OpenAI quota exceeded)"
                governance_analysis = "Rule-based analysis (OpenAI quota exceeded)"
                ai_thesis = "Rule-based thesis (OpenAI quota exceeded)"
        else:
            print(f"  ℹ️  No LLM API key found - using rule-based analysis")
            financial_analysis = "Rule-based analysis (add LLM key for AI analysis)"
            governance_analysis = "Rule-based analysis (add LLM key for AI analysis)"
            ai_thesis = "Rule-based thesis (add LLM key for AI-generated thesis)"
        
        processing_time = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"✅ ANALYSIS COMPLETE in {processing_time:.1f}s")
        print(f"{'='*70}\n")
        
        return {
            'ticker': ticker,
            'company_name': fetcher.company_name,
            'filings': filings,
            'extracted_data': extracted_data,
            'metrics': metrics,
            'red_flags': red_flags,
            'peer_comparison': peer_comparison,
            'basic_thesis': basic_thesis,
            'financial_analysis': financial_analysis,
            'governance_analysis': governance_analysis,
            'ai_thesis': ai_thesis,
            'processing_time': processing_time
        }
    
    def _generate_basic_thesis(self, ticker, company_name, metrics, red_flags, peer_comp, extracted_data):
        """Generate basic rule-based investment thesis"""
        
        # Calculate key metrics for thesis
        revenue = extracted_data['10k']['revenue_current']
        market_cap = extracted_data['market_data']['market_cap']
        
        thesis = f"""# Investment Thesis: {company_name} ({ticker})

## Executive Summary

{company_name} presents {'a compelling' if len(red_flags) >= 2 else 'an interesting'} activist investment opportunity with **{len(red_flags)} identified value creation catalyst{'s' if len(red_flags) != 1 else ''}**.

**Key Financial Metrics:**
- **Revenue:** ${revenue/1e9:.1f}B (Growth: {metrics.revenue_growth_1y:+.1f}% YoY)
- **Market Cap:** ${market_cap/1e9:.1f}B
- **ROE:** {metrics.roe:.1f}% (Peer {peer_comp.roe_percentile:.0f}th percentile)
- **ROIC:** {metrics.roic:.1f}% (Peer {peer_comp.roic_percentile:.0f}th percentile)
- **Operating Margin:** {metrics.operating_margin:.1f}% (Peer {peer_comp.margin_percentile:.0f}th percentile)

**Investment Opportunity:**
Based on peer valuation analysis, {ticker} trades at a {abs(peer_comp.upside_to_peer_median):.1f}% {'discount' if peer_comp.upside_to_peer_median > 0 else 'premium'} to peer median multiples.

---

## Value Creation Opportunities

"""
        
        # Add red flags as catalysts
        if red_flags:
            for i, (flag_name, flag_desc) in enumerate(red_flags.items(), 1):
                catalyst_name = flag_name.replace('_', ' ').title()
                thesis += f"""### Catalyst {i}: {catalyst_name}

**Current State:** {flag_desc}

**Proposed Action:** Address this operational inefficiency through targeted improvements.

---

"""
        else:
            thesis += """*No major red flags identified. Company appears well-managed on core financial metrics.*

"""
        
        thesis += f"""## Conclusion

{company_name} represents {'a compelling' if len(red_flags) >= 2 else 'an interesting'} activist opportunity.

**Recommendation:** {'Initiate position and engage with management/board' if red_flags else 'Monitor for future opportunities'}
"""
        
        return thesis


def save_results(results: Dict, output_file: str = None):
    """Save analysis results to file"""
    
    if output_file is None:
        output_file = f"analysis_{results['ticker']}_{int(time.time())}.md"
    
    with open(output_file, 'w') as f:
        f.write("# SHAREHOLDER CATALYST ANALYSIS REPORT\n\n")
        f.write(f"**Company:** {results['company_name']} ({results['ticker']})\n")
        f.write(f"**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Processing Time:** {results['processing_time']:.1f}s\n\n")
        
        f.write("---\n\n")
        
        # Write AI thesis if available
        if results['ai_thesis'] and results['ai_thesis'] != "AI thesis not available (no API key)":
            f.write("# AI-GENERATED INVESTMENT THESIS\n\n")
            f.write(results['ai_thesis'])
            f.write("\n\n---\n\n")
        
        # Write basic thesis
        f.write("# BASIC INVESTMENT THESIS\n\n")
        f.write(results['basic_thesis'])
        f.write("\n\n---\n\n")
        
        # Write financial analysis
        if results['financial_analysis'] and results['financial_analysis'] != "AI analysis not available (no API key)":
            f.write("# DETAILED FINANCIAL ANALYSIS\n\n")
            f.write(results['financial_analysis'])
            f.write("\n\n---\n\n")
        
        # Write governance analysis
        if results['governance_analysis'] and results['governance_analysis'] != "AI analysis not available (no API key)":
            f.write("# DETAILED GOVERNANCE ANALYSIS\n\n")
            f.write(results['governance_analysis'])
    
    print(f"\n💾 Results saved to: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    
    # Get ticker from command line
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py TICKER")
        print("Example: python orchestrator.py AAPL")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    
    # Run analysis
    orchestrator = ActivistIntelOrchestrator()
    result = asyncio.run(orchestrator.analyze_company(ticker))
    
    # Save results
    output_file = save_results(result)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print(f"\nView your report: {output_file}\n")
