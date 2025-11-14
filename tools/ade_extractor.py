"""
LandingAI SDK-Based Document Extractor
Uses official landingai-ade Python library from hackathon
Converts HTML SEC filings to markdown for LandingAI processing
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class LandingAISDKExtractor:
    """Extract structured data from SEC filings using LandingAI official SDK"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.client = None
        self.current_ticker = None
        
        # Initialize client if API key provided
        if api_key:
            try:
                from landingai_ade import LandingAIADE
                self.client = LandingAIADE(apikey=api_key)
                print("    ✅ LandingAI SDK initialized")
            except ImportError:
                print("    ⚠️  landingai-ade not installed. Run: pip install landingai-ade")
                self.client = None
            except Exception as e:
                print(f"    ⚠️  Error initializing LandingAI: {str(e)}")
                self.client = None
    
    def _html_to_markdown(self, html_path: str) -> str:
        """Convert HTML file to markdown text for LandingAI processing"""
        try:
            from bs4 import BeautifulSoup
            import html2text
            
            # Read the HTML file
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Convert HTML to markdown/text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            h.body_width = 0  # Don't wrap lines
            
            markdown_text = h.handle(html_content)
            
            # Save as markdown file
            md_path = html_path.replace('.html', '.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            return md_path
            
        except ImportError as e:
            print(f"      ⚠️  Missing dependencies. Run: pip install beautifulsoup4 html2text")
            return None
        except Exception as e:
            print(f"      ⚠️  Error converting HTML to markdown: {str(e)}")
            return None
    
    async def process_all_documents(self, filings: Dict) -> Dict:
        """
        Process all SEC filings and extract structured data
        
        Args:
            filings: Dictionary of filing types and their documents
            
        Returns:
            Dictionary with extracted financial and governance data
        """
        
        print("  🤖 Starting LandingAI document extraction...")
        
        # Store ticker for demo mode
        for filing_type, docs in filings.items():
            if docs and len(docs) > 0:
                import re
                ticker_match = re.search(r'([A-Z]+)_', os.path.basename(docs[0].get('path', '')))
                if ticker_match:
                    self.current_ticker = ticker_match.group(1)
                break
        
        # If no SDK client, use demo mode
        if not self.client:
            print("    ⚠️  No API key provided - using comprehensive demo data")
            return self._get_complete_demo_data()
        
        # Process documents with SDK
        tasks = []
        
        if '10-K' in filings and filings['10-K']:
            tasks.append(self._extract_10k_async(filings['10-K']))
        
        if 'DEF 14A' in filings and filings['DEF 14A']:
            tasks.append(self._extract_proxy_async(filings['DEF 14A']))
        
        if '8-K' in filings and filings['8-K']:
            tasks.append(self._extract_8k_async(filings['8-K']))
        
        if not tasks:
            print("    ⚠️  No filings to process, using demo data")
            return self._get_complete_demo_data()
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined = {}
        for result in results:
            if isinstance(result, dict):
                combined.update(result)
            elif isinstance(result, Exception):
                print(f"    ⚠️  Error during extraction: {str(result)}")
        
        # Ensure required fields
        combined = self._ensure_required_fields(combined)
        
        return combined
    
    async def _extract_10k_async(self, filings: List[Dict]) -> Dict:
        """Async extraction of 10-K data"""
        return await asyncio.to_thread(self.extract_10k_data, filings)
    
    async def _extract_proxy_async(self, filings: List[Dict]) -> Dict:
        """Async extraction of proxy data"""
        return await asyncio.to_thread(self.extract_proxy_data, filings)
    
    async def _extract_8k_async(self, filings: List[Dict]) -> Dict:
        """Async extraction of 8-K data"""
        return await asyncio.to_thread(self.extract_8k_data, filings)
    
    def extract_10k_data(self, filings: List[Dict]) -> Dict:
        """Extract financial data from 10-K filings using SDK"""
        
        print("    📊 Extracting 10-K financial data...")
        
        if not filings or not self.client:
            return {'10k': self._get_default_10k_data()}
        
        filing = filings[0]  # Most recent
        
        try:
            file_path = filing['path']
            
            # Convert HTML to markdown if needed
            if file_path.lower().endswith('.html'):
                print(f"      🔄 Converting HTML to markdown for LandingAI...")
                md_path = self._html_to_markdown(file_path)
                if not md_path:
                    print(f"      ⚠️  Conversion failed, using defaults")
                    return {'10k': self._get_default_10k_data()}
                file_path = md_path
                print(f"      ✅ Converted to markdown")
            
            # For markdown files, directly use them for extraction
            print(f"      🔍 Extracting financial metrics with LandingAI...")
            
            # Define extraction schema
            from landingai_ade.lib import pydantic_to_json_schema
            
            class FinancialData(BaseModel):
                revenue_current: float = Field(description="Most recent fiscal year total revenue in dollars")
                revenue_prior_1: float = Field(description="Prior fiscal year total revenue in dollars")
                operating_income: float = Field(description="Operating income for current year in dollars")
                net_income_current: float = Field(description="Net income for current year in dollars")
                total_assets: float = Field(description="Total assets in dollars")
                total_liabilities: float = Field(description="Total liabilities in dollars")
                shareholders_equity: float = Field(description="Shareholders equity in dollars")
                cash_equivalents: float = Field(description="Cash and cash equivalents in dollars")
                total_debt: float = Field(description="Total debt (long-term + short-term) in dollars")
                shares_outstanding: float = Field(description="Basic shares outstanding")
            
            schema = pydantic_to_json_schema(FinancialData)
            
            # Extract structured data directly from markdown
            extract_result = self.client.extract(
                schema=schema,
                markdown=Path(file_path)
            )
            
            extraction = extract_result.extraction
            
            print(f"      ✅ Successfully extracted 10-K data with LandingAI SDK")
            
            # Convert to our format
            return {'10k': {
                'revenue_current': extraction.get('revenue_current', 0),
                'revenue_prior_1': extraction.get('revenue_prior_1', 0),
                'revenue_prior_2': 0,
                'operating_income': extraction.get('operating_income', 0),
                'net_income_current': extraction.get('net_income_current', 0),
                'net_income_prior_1': 0,
                'total_assets': extraction.get('total_assets', 0),
                'total_liabilities': extraction.get('total_liabilities', 0),
                'shareholders_equity': extraction.get('shareholders_equity', 0),
                'cash_equivalents': extraction.get('cash_equivalents', 0),
                'total_debt': extraction.get('total_debt', 0),
                'shares_outstanding': extraction.get('shares_outstanding', 0)
            }}
            
        except Exception as e:
            print(f"      ⚠️  Error extracting 10-K: {str(e)}")
            return {'10k': self._get_default_10k_data()}
    
    def extract_proxy_data(self, filings: List[Dict]) -> Dict:
        """Extract governance data from proxy statements using SDK"""
        
        print("    👔 Extracting proxy statement data...")
        
        if not filings or not self.client:
            return {'proxy': self._get_default_proxy_data()}
        
        filing = filings[0]  # Most recent
        
        try:
            file_path = filing['path']
            
            # Convert HTML to markdown if needed
            if file_path.lower().endswith('.html'):
                print(f"      🔄 Converting HTML to markdown for LandingAI...")
                md_path = self._html_to_markdown(file_path)
                if not md_path:
                    print(f"      ⚠️  Conversion failed, using defaults")
                    return {'proxy': self._get_default_proxy_data()}
                file_path = md_path
                print(f"      ✅ Converted to markdown")
            
            # Define schema
            from landingai_ade.lib import pydantic_to_json_schema
            
            class BoardMember(BaseModel):
                name: str = Field(description="Director name")
                independent: bool = Field(description="Whether director is independent")
                tenure_years: float = Field(description="Years serving on board")
            
            class ProxyData(BaseModel):
                ceo_total_comp: float = Field(description="CEO total compensation in dollars")
                ceo_base_salary: float = Field(description="CEO base salary in dollars")
                say_on_pay_approval_pct: float = Field(description="Say-on-pay approval percentage (0-100)")
                board_size: int = Field(description="Number of board members")
                independent_directors: int = Field(description="Number of independent directors")
                board_members: List[BoardMember] = Field(description="List of board members with details")
            
            schema = pydantic_to_json_schema(ProxyData)
            
            # Extract
            print(f"      🔍 Extracting governance metrics with LandingAI...")
            
            extract_result = self.client.extract(
                schema=schema,
                markdown=Path(file_path)
            )
            
            extraction = extract_result.extraction
            
            print(f"      ✅ Successfully extracted proxy data with LandingAI SDK")
            
            # Calculate average tenure
            board_members = extraction.get('board_members', [])
            avg_tenure = 0
            if board_members:
                tenures = [m.get('tenure_years', 0) for m in board_members]
                avg_tenure = sum(tenures) / len(tenures) if tenures else 0
            
            return {'proxy': {
                'ceo_total_comp_current': extraction.get('ceo_total_comp', 0),
                'ceo_total_comp_prior_1': 0,
                'ceo_base_salary': extraction.get('ceo_base_salary', 0),
                'ceo_bonus': 0,
                'ceo_stock_awards': 0,
                'say_on_pay_approval_pct': extraction.get('say_on_pay_approval_pct', 0),
                'board_size': extraction.get('board_size', 0),
                'independent_directors': extraction.get('independent_directors', 0),
                'average_director_tenure': avg_tenure,
                'board_members': board_members
            }}
            
        except Exception as e:
            print(f"      ⚠️  Error extracting proxy: {str(e)}")
            return {'proxy': self._get_default_proxy_data()}
    
    def extract_8k_data(self, filings: List[Dict]) -> Dict:
        """Extract recent events from 8-K filings"""
        
        print("    📋 Extracting 8-K event data...")
        
        # For 8-Ks, simple text extraction is sufficient
        events = []
        
        try:
            for filing in filings[:3]:  # Recent 3
                # Just note that event exists
                events.append(f"Material event on {filing.get('date', 'unknown date')}")
            
            return {'8k': {'recent_events': events}}
            
        except Exception as e:
            print(f"      ⚠️  Error extracting 8-K: {str(e)}")
            return {'8k': {'recent_events': []}}
    
    def _ensure_required_fields(self, data: Dict) -> Dict:
        """Ensure all required fields exist"""
        
        if '10k' not in data:
            data['10k'] = self._get_default_10k_data()
        
        if 'proxy' not in data:
            data['proxy'] = self._get_default_proxy_data()
        
        if '8k' not in data:
            data['8k'] = {'recent_events': []}
        
        return data
    
    def _get_default_10k_data(self) -> Dict:
        """Return default 10-K data structure"""
        return {
            'revenue_current': 0,
            'revenue_prior_1': 0,
            'revenue_prior_2': 0,
            'operating_income': 0,
            'net_income_current': 0,
            'net_income_prior_1': 0,
            'total_assets': 0,
            'total_liabilities': 0,
            'shareholders_equity': 0,
            'cash_equivalents': 0,
            'total_debt': 0,
            'shares_outstanding': 0
        }
    
    def _get_default_proxy_data(self) -> Dict:
        """Return default proxy data structure"""
        return {
            'ceo_total_comp_current': 0,
            'ceo_total_comp_prior_1': 0,
            'ceo_base_salary': 0,
            'ceo_bonus': 0,
            'ceo_stock_awards': 0,
            'say_on_pay_approval_pct': 0,
            'board_size': 0,
            'independent_directors': 0,
            'average_director_tenure': 0,
            'board_members': []
        }
    
    def _get_complete_demo_data(self) -> Dict:
        """Return demo data for testing without API"""
        
        demo_companies = {
            'AAPL': {
                '10k': {
                    'revenue_current': 383285000000,
                    'revenue_prior_1': 394328000000,
                    'revenue_prior_2': 365817000000,
                    'operating_income': 114301000000,
                    'net_income_current': 96995000000,
                    'net_income_prior_1': 99803000000,
                    'total_assets': 352755000000,
                    'total_liabilities': 290437000000,
                    'shareholders_equity': 62146000000,
                    'cash_equivalents': 29965000000,
                    'total_debt': 111088000000,
                    'shares_outstanding': 15441880000
                },
                'proxy': {
                    'ceo_total_comp_current': 63209230,
                    'ceo_total_comp_prior_1': 99420000,
                    'ceo_base_salary': 3000000,
                    'ceo_bonus': 0,
                    'ceo_stock_awards': 52000000,
                    'say_on_pay_approval_pct': 95.4,
                    'board_size': 8,
                    'independent_directors': 7,
                    'average_director_tenure': 12.5,
                    'board_members': [
                        {"name": "Tim Cook", "role": "CEO", "independent": False, "tenure_years": 12}
                    ]
                },
                '8k': {'recent_events': ['Q4 earnings release', 'Product announcement']}
            }
        }
        
        ticker = self.current_ticker or 'AAPL'
        return demo_companies.get(ticker, demo_companies['AAPL'])


# Backwards compatibility - keep old class name
class LandingAIDirectExtractor(LandingAISDKExtractor):
    """Alias for backwards compatibility"""
    pass
