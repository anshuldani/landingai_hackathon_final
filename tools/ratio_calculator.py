"""
Financial Ratio Calculator
Calculates key metrics for activist analysis
"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class FinancialMetrics:
    """Container for calculated financial metrics"""
    market_cap: float
    enterprise_value: float
    ev_to_revenue: float
    roe: float
    roic: float
    operating_margin: float
    revenue_growth_1y: float
    cash_to_assets_ratio: float


class RatioCalculator:
    """Calculate financial ratios from extracted SEC filing data"""
    
    def __init__(self):
        self.metrics = None
    
    def calculate_all_ratios(self, extracted_data: Dict) -> FinancialMetrics:
        """Calculate comprehensive financial ratios"""
        
        financial_data = extracted_data.get('10k', {})
        market_data = extracted_data.get('market_data', {})
        
        # Extract base values
        revenue = financial_data.get('revenue_current', 0)
        revenue_prior = financial_data.get('revenue_prior_1', 0)
        net_income = financial_data.get('net_income_current', 0)
        total_assets = financial_data.get('total_assets', 0)
        total_debt = financial_data.get('total_debt', 0)
        cash = financial_data.get('cash_equivalents', 0)
        equity = financial_data.get('shareholders_equity', 0)
        operating_income = financial_data.get('operating_income', 0)
        market_cap = market_data.get('market_cap', 0)
        
        # Calculate metrics
        enterprise_value = market_cap + (total_debt - cash)
        invested_capital = total_debt + equity
        
        self.metrics = FinancialMetrics(
            market_cap=market_cap,
            enterprise_value=enterprise_value,
            ev_to_revenue=self._safe_divide(enterprise_value, revenue),
            roe=self._safe_divide(net_income, equity) * 100,
            roic=self._safe_divide(operating_income * 0.79, invested_capital) * 100,
            operating_margin=self._safe_divide(operating_income, revenue) * 100,
            revenue_growth_1y=self._calculate_growth(revenue, revenue_prior),
            cash_to_assets_ratio=self._safe_divide(cash, total_assets) * 100
        )
        
        return self.metrics
    
    def get_activist_red_flags(self, metrics: FinancialMetrics) -> Dict[str, str]:
        """Identify potential activist red flags"""
        red_flags = {}
        
        if metrics.roic < 10:
            red_flags['low_roic'] = f"🔴 ROIC of {metrics.roic:.1f}% below threshold"
        
        if metrics.cash_to_assets_ratio > 30:
            red_flags['excess_cash'] = f"🟡 Cash is {metrics.cash_to_assets_ratio:.1f}% of assets"
        
        if metrics.roe < 10:
            red_flags['low_roe'] = f"🔴 ROE of {metrics.roe:.1f}% indicates poor returns"
        
        if metrics.revenue_growth_1y < -5:
            red_flags['revenue_decline'] = f"🔴 Revenue declined {metrics.revenue_growth_1y:.1f}% YoY"
        
        if metrics.operating_margin < 10:
            red_flags['low_margins'] = f"🔴 Operating margin of {metrics.operating_margin:.1f}% below industry standards"
        
        return red_flags
    
    def _safe_divide(self, num: float, denom: float) -> float:
        return num / denom if denom != 0 else 0
    
    def _calculate_growth(self, current: float, prior: float) -> float:
        if prior == 0:
            return 0
        return ((current - prior) / prior) * 100


if __name__ == "__main__":
    # Test
    sample_data = {
        '10k': {
            'revenue_current': 26000000000,
            'revenue_prior_1': 24500000000,
            'net_income_current': 3200000000,
            'total_assets': 45000000000,
            'total_debt': 12000000000,
            'cash_equivalents': 8000000000,
            'shareholders_equity': 28000000000,
            'operating_income': 5500000000
        },
        'market_data': {
            'market_cap': 72750000000
        }
    }
    
    calc = RatioCalculator()
    metrics = calc.calculate_all_ratios(sample_data)
    print(f"ROE: {metrics.roe:.1f}%")
    print(f"ROIC: {metrics.roic:.1f}%")
    print(f"EV/Revenue: {metrics.ev_to_revenue:.1f}x")
