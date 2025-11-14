"""
Governance Analyst Agent - OpenAI Implementation
Uses OpenAI GPT-4 for corporate governance analysis
"""

import openai
import json
from typing import Dict

class GovernanceAnalystAgent:
    """Analyzes corporate governance and compensation practices"""
    
    def __init__(self, api_key: str):
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"  # Latest GPT-4 model
        else:
            self.client = None
            self.model = None
    
    def analyze(self, extracted_data: dict) -> str:
        """
        Run comprehensive governance analysis on extracted proxy data
        
        Returns detailed markdown analysis of governance issues
        """
        
        print("  👔 Running governance analysis with GPT-4...")
        
        if not self.client:
            return self._fallback_analysis(extracted_data.get('proxy', {}))
        
        # Prepare data for analysis
        proxy_data = extracted_data.get('proxy', {})
        financial_data = extracted_data.get('10k', {})
        market_data = extracted_data.get('market_data', {})
        
        # Create analysis prompt
        prompt = self._build_analysis_prompt(proxy_data, financial_data, market_data)
        
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
                temperature=0.3,
                max_tokens=4096
            )
            
            analysis = response.choices[0].message.content
            print("    ✅ Governance analysis complete")
            return analysis
            
        except Exception as e:
            print(f"    ⚠️ Error in governance analysis: {str(e)}")
            return self._fallback_analysis(proxy_data)
    
    def _get_system_prompt(self) -> str:
        """System prompt for governance analysis"""
        return """You are an expert corporate governance analyst specializing in activist investing.

Your role is to identify governance red flags and compensation misalignments that activist investors can target.

Focus on:
1. **Board Composition:** Independence, tenure, diversity, expertise gaps
2. **Executive Compensation:** Pay-for-performance alignment, excessive awards
3. **Shareholder Rights:** Voting rights, poison pills, staggered boards
4. **Related Party Transactions:** Self-dealing, conflicts of interest
5. **Say-on-Pay Results:** Shareholder approval trends

Be direct and critical. Call out specific issues with names and numbers.
Compare to best practices (e.g., majority independent boards, <10 year CEO tenure).

Output in markdown with:
- Clear section headers
- Bold key findings and names
- Specific governance violations or weaknesses
- Actionable recommendations for activist campaigns"""
    
    def _build_analysis_prompt(self, proxy_data: Dict, financial_data: Dict, market_data: Dict) -> str:
        """Build analysis prompt with governance data"""
        
        ceo_comp_current = proxy_data.get('ceo_total_comp_current', 0)
        ceo_comp_prior = proxy_data.get('ceo_total_comp_prior_1', 0)
        board_members = proxy_data.get('board_members', [])
        say_on_pay = proxy_data.get('say_on_pay_approval_pct', 0)
        
        net_income = financial_data.get('net_income_current', 0)
        revenue = financial_data.get('revenue_current', 0)
        market_cap = market_data.get('market_cap', 0)
        
        # Calculate pay ratios
        pay_as_pct_of_income = (ceo_comp_current / net_income * 100) if net_income else 0
        pay_change = ((ceo_comp_current - ceo_comp_prior) / ceo_comp_prior * 100) if ceo_comp_prior else 0
        
        # Format board table
        board_table = "\n".join([
            f"  - **{m.get('name', 'Unknown')}**: {m.get('role', 'Director')}, "
            f"{m.get('tenure_years', 0)} years, "
            f"{'Independent' if m.get('independent') else 'Not Independent'}"
            for m in board_members
        ])
        
        return f"""Analyze the following corporate governance data from an activist investor perspective:

**Executive Compensation:**
- CEO Total Compensation (Current): ${ceo_comp_current:,.0f}
- CEO Total Compensation (Prior Year): ${ceo_comp_prior:,.0f}
- Year-over-Year Change: {pay_change:+.1f}%
- CEO Pay as % of Net Income: {pay_as_pct_of_income:.2f}%

**Say-on-Pay Vote:**
- Shareholder Approval Rate: {say_on_pay:.1f}%

**Board of Directors:**
{board_table if board_table else "  - Board composition data not available"}

**Company Performance Context:**
- Net Income: ${net_income:,.0f}
- Revenue: ${revenue:,.0f}
- Market Cap: ${market_cap:,.0f}

**Your Analysis Task:**

1. **Executive Compensation Analysis**
   - Is CEO pay aligned with performance?
   - Compare compensation to shareholder returns
   - Identify excessive or unjustified awards
   - Recommend pay structure changes

2. **Board Composition Review**
   - Evaluate board independence (benchmark: >80% independent)
   - Assess director tenure (red flag: >15 years indicates entrenchment)
   - Identify expertise gaps or outdated skillsets
   - Recommend board refreshment plan

3. **Shareholder Rights Assessment**
   - Evaluate say-on-pay results (concern if <85%)
   - Note any anti-takeover provisions
   - Identify governance practices that harm shareholders

4. **Activist Campaign Strategy**
   - Prioritize the most egregious governance issues
   - Quantify cost to shareholders
   - Outline specific board changes or compensation reforms
   - Estimate potential value creation from governance improvements

Be specific with names, numbers, and recommendations. This is for an activist proxy fight."""
    
    def _fallback_analysis(self, proxy_data: Dict) -> str:
        """Fallback analysis if API call fails"""
        
        ceo_comp = proxy_data.get('ceo_total_comp_current', 0)
        say_on_pay = proxy_data.get('say_on_pay_approval_pct', 0)
        
        return f"""## Governance Analysis (Fallback Mode)

### Executive Compensation
- CEO Compensation: ${ceo_comp/1e6:.1f}M
- Say-on-Pay Approval: {say_on_pay:.1f}%

### Key Observations
- Governance data extracted successfully
- Detailed analysis requires API access
- Manual review recommended

*Note: This is a simplified analysis. For full activist-grade analysis, ensure API keys are configured.*
"""
