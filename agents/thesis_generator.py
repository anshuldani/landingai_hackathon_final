"""
Thesis Generator Agent - OpenAI Implementation
Uses OpenAI GPT-4 to synthesize analyses into activist investment thesis
"""

import openai
import json
from typing import Dict

class ThesisGeneratorAgent:
    """Synthesizes analyses into activist investment thesis"""
    
    def __init__(self, api_key: str):
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"  # Latest GPT-4 model
        else:
            self.client = None
            self.model = None
    
    def generate_thesis(self, financial_analysis: str, governance_analysis: str, 
                       company_name: str, ticker: str, extracted_data: dict) -> str:
        """
        Generate complete activist investment thesis
        
        Args:
            financial_analysis: Output from FinancialAnalystAgent
            governance_analysis: Output from GovernanceAnalystAgent
            company_name: Company name
            ticker: Stock ticker
            extracted_data: Raw extracted data for context
            
        Returns:
            Complete investment thesis in markdown
        """
        
        print("  📝 Generating investment thesis with GPT-4...")
        
        if not self.client:
            return self._fallback_thesis(company_name, ticker)
        
        # Build comprehensive prompt
        prompt = self._build_thesis_prompt(
            financial_analysis, 
            governance_analysis, 
            company_name, 
            ticker,
            extracted_data
        )
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,  # Slightly higher for creative synthesis
                max_tokens=6000
            )
            
            thesis = response.choices[0].message.content
            print("    ✅ Investment thesis generated")
            return thesis
            
        except Exception as e:
            print(f"    ⚠️ Error generating thesis: {str(e)}")
            return self._fallback_thesis(company_name, ticker)
    
    def _get_system_prompt(self) -> str:
        """System prompt for thesis generation"""
        return """You are a senior analyst at an activist investment fund, preparing a comprehensive investment thesis.

Your role is to synthesize financial and governance analyses into a compelling, actionable activist thesis.

Structure your thesis with:

# Investment Thesis: [COMPANY] ([TICKER])

## Executive Summary
2-3 paragraphs covering:
- The opportunity (what's broken)
- The solution (specific activist campaign)
- The return potential (price target, timeline)

## Value Creation Opportunities
For each catalyst (3-5 total):
### Catalyst N: [Name]
- **Current State:** What's wrong now
- **Proposed Action:** Specific steps (1-3 bullet points)
- **Value Impact:** Quantified impact ($ per share or % upside)
- **Timeline:** How long to realize

## Proposed Action Plan
### Phase 1: Engagement (Months 1-3)
### Phase 2: Implementation (Months 3-12)
### Phase 3: Value Realization (Months 12-24)

## Valuation & Return Potential
- Current valuation
- Target valuation with rationale
- Base case and bull case scenarios

## Risk Factors
3-5 key risks to the thesis

## Conclusion
Clear recommendation: Initiate position or Pass

Be direct, quantitative, and action-oriented. Use bold for key findings.
This is for LP presentation and internal investment committee."""
    
    def _build_thesis_prompt(self, financial_analysis: str, governance_analysis: str,
                            company_name: str, ticker: str, extracted_data: dict) -> str:
        """Build thesis generation prompt"""
        
        # Extract key metrics for context
        financial_data = extracted_data.get('10k', {})
        market_data = extracted_data.get('market_data', {})
        
        revenue = financial_data.get('revenue_current', 0)
        market_cap = market_data.get('market_cap', 0)
        current_price = market_data.get('current_price', 0)
        
        return f"""Synthesize the following analyses into a comprehensive activist investment thesis:

**Company:** {company_name} ({ticker})
**Current Price:** ${current_price:.2f}
**Market Cap:** ${market_cap/1e9:.1f}B
**Revenue:** ${revenue/1e9:.1f}B

---

## FINANCIAL ANALYSIS
{financial_analysis}

---

## GOVERNANCE ANALYSIS
{governance_analysis}

---

**Your Task:**

Synthesize these analyses into a compelling activist investment thesis. 

Requirements:
1. **Executive Summary** - Make it punchy and investor-ready
2. **Value Creation Catalysts** - Identify 3-5 specific, actionable opportunities
3. **Action Plan** - Timeline with specific milestones
4. **Valuation** - Target price with clear methodology
5. **Risks** - Be honest about what could go wrong
6. **Recommendation** - Clear buy/pass decision

Focus on:
- Specific numbers and percentages
- Concrete actions (not vague suggestions)
- Realistic timelines (12-24 months)
- Quantified value creation ($ per share)

This thesis will be presented to the investment committee and potentially to the board of {company_name}."""
    
    def _fallback_thesis(self, company_name: str, ticker: str) -> str:
        """Fallback thesis if API call fails"""
        
        return f"""# Investment Thesis: {company_name} ({ticker})

## Executive Summary

Analysis of {company_name} has been completed. Detailed synthesis requires API access for full thesis generation.

## Key Findings
- Financial data extracted successfully
- Governance data reviewed
- Full thesis generation pending API configuration

## Next Steps
Configure OpenAI API key to generate complete investment thesis.

*Note: This is a placeholder. For full activist-grade thesis, ensure API keys are configured.*
"""
