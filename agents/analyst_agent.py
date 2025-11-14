"""
Financial Analyst Agent - OpenAI Implementation
Uses OpenAI GPT-4 for real financial analysis
"""

import openai
import json
from typing import Dict

class FinancialAnalystAgent:
    """Analyzes financial performance and identifies value gaps"""
    
    def __init__(self, api_key: str):
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"  # Latest GPT-4 model
        else:
            self.client = None
            self.model = None
    
    def analyze(self, extracted_data: dict) -> str:
        """
        Run comprehensive financial analysis on extracted data
        
        Returns detailed markdown analysis
        """
        
        print("  💰 Running financial analysis with GPT-4...")
        
        if not self.client:
            return self._fallback_analysis(extracted_data.get('10k', {}), extracted_data.get('market_data', {}))
        
        # Prepare data for analysis
        financial_data = extracted_data.get('10k', {})
        market_data = extracted_data.get('market_data', {})
        
        # Create analysis prompt
        prompt = self._build_analysis_prompt(financial_data, market_data)
        
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
                temperature=0.3,  # Lower temperature for analytical work
                max_tokens=4096
            )
            
            analysis = response.choices[0].message.content
            print("    ✅ Financial analysis complete")
            return analysis
            
        except Exception as e:
            print(f"    ⚠️ Error in financial analysis: {str(e)}")
            return self._fallback_analysis(financial_data, market_data)
    
    def _get_system_prompt(self) -> str:
        """System prompt for financial analysis"""
        return """You are an expert financial analyst specializing in activist investing.

Your role is to analyze company financials and identify value creation opportunities.

Focus on:
1. **Capital Efficiency:** ROE, ROIC, asset turnover
2. **Cash Position:** Excess cash, debt levels, working capital
3. **Profitability Trends:** Margin compression/expansion, cost structure
4. **Valuation Gaps:** Trading multiples vs intrinsic value
5. **Hidden Value:** Undervalued assets, non-core business units

Be quantitative. Cite specific numbers. Compare to industry benchmarks.
Identify concrete red flags that activist investors can target.

Output in markdown with:
- Clear section headers
- Bold key findings
- Bullet points for specific issues
- Quantified value creation opportunities"""
    
    def _build_analysis_prompt(self, financial_data: Dict, market_data: Dict) -> str:
        """Build analysis prompt with financial data"""
        
        revenue_current = financial_data.get('revenue_current', 0)
        revenue_prior_1 = financial_data.get('revenue_prior_1', 0)
        net_income = financial_data.get('net_income_current', 0)
        total_assets = financial_data.get('total_assets', 0)
        cash = financial_data.get('cash_equivalents', 0)
        debt = financial_data.get('total_debt', 0)
        equity = financial_data.get('shareholders_equity', 0)
        operating_income = financial_data.get('operating_income', 0)
        market_cap = market_data.get('market_cap', 0)
        
        # Calculate key ratios
        roe = (net_income / equity * 100) if equity else 0
        roa = (net_income / total_assets * 100) if total_assets else 0
        debt_to_equity = (debt / equity) if equity else 0
        cash_to_assets = (cash / total_assets * 100) if total_assets else 0
        operating_margin = (operating_income / revenue_current * 100) if revenue_current else 0
        revenue_growth = ((revenue_current - revenue_prior_1) / revenue_prior_1 * 100) if revenue_prior_1 else 0
        
        return f"""Analyze the following company financials from an activist investor perspective:

**Income Statement:**
- Revenue (Current Year): ${revenue_current:,.0f}
- Revenue (Prior Year): ${revenue_prior_1:,.0f}
- Revenue Growth: {revenue_growth:.1f}%
- Operating Income: ${operating_income:,.0f}
- Operating Margin: {operating_margin:.1f}%
- Net Income: ${net_income:,.0f}

**Balance Sheet:**
- Total Assets: ${total_assets:,.0f}
- Cash & Equivalents: ${cash:,.0f} ({cash_to_assets:.1f}% of assets)
- Total Debt: ${debt:,.0f}
- Shareholders' Equity: ${equity:,.0f}
- Debt-to-Equity: {debt_to_equity:.2f}x

**Market Data:**
- Market Capitalization: ${market_cap:,.0f}

**Key Ratios:**
- Return on Equity (ROE): {roe:.1f}%
- Return on Assets (ROA): {roa:.1f}%

**Your Analysis Task:**

1. **Capital Efficiency Analysis**
   - Evaluate ROE and ROIC performance
   - Assess if capital is being deployed efficiently
   - Identify opportunities to improve returns

2. **Cash & Capital Structure**
   - Is the company holding excess cash?
   - Is the balance sheet optimized?
   - Potential for shareholder returns (dividends, buybacks)?

3. **Operational Performance**
   - Analyze margin trends
   - Identify cost structure issues
   - Compare to industry benchmarks (assume tech industry, 30-40% operating margins)

4. **Value Creation Opportunities**
   - Quantify potential value unlocks
   - Suggest specific activist campaigns
   - Estimate dollar impact per share

Format your response as a detailed markdown report with specific, actionable findings."""
    
    def _fallback_analysis(self, financial_data: Dict, market_data: Dict) -> str:
        """Fallback analysis if API call fails"""
        
        revenue = financial_data.get('revenue_current', 0)
        net_income = financial_data.get('net_income_current', 0)
        
        return f"""## Financial Analysis (Fallback Mode)

### Overview
Company generated ${revenue/1e9:.1f}B in revenue with ${net_income/1e9:.1f}B in net income.

### Key Observations
- Financial data extracted successfully
- Detailed analysis requires API access
- Manual review recommended

*Note: This is a simplified analysis. For full activist-grade analysis, ensure API keys are configured.*
"""
