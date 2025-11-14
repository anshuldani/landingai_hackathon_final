#!/usr/bin/env python3
"""
Shareholder Catalyst - System Validation Script
Tests all components and ensures production readiness
"""

import os
import sys
import asyncio
import json
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama for colored output
init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.BLUE}{'='*60}")
    print(f"{Fore.BLUE}{text}")
    print(f"{Fore.BLUE}{'='*60}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.CYAN}ℹ️  {text}{Style.RESET_ALL}")

class SystemValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
        self.test_ticker = 'AAPL'  # Default test ticker
        
    def validate_environment(self):
        """Check environment setup"""
        print_header("ENVIRONMENT VALIDATION")
        
        # Check Python version
        py_version = sys.version_info
        if py_version.major >= 3 and py_version.minor >= 8:
            print_success(f"Python {py_version.major}.{py_version.minor} installed")
        else:
            print_error(f"Python 3.8+ required, found {py_version.major}.{py_version.minor}")
            self.errors.append("Python version incompatible")
        
        # Check .env file
        if os.path.exists('.env'):
            print_success(".env file found")
            load_dotenv()
        else:
            print_warning(".env file not found - using defaults")
            self.warnings.append("No .env file")
        
        # Check API keys
        landing_key = os.getenv('LANDING_AI_API_KEY') or os.getenv('VISION_AGENT_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if landing_key:
            print_success("LandingAI API key configured")
        else:
            print_warning("LandingAI API key not found - will use demo mode")
            self.warnings.append("No LandingAI key")
        
        if openai_key:
            print_success("OpenAI API key configured")
        else:
            print_warning("OpenAI API key not found - will use rule-based analysis")
            self.warnings.append("No OpenAI key")
    
    def validate_dependencies(self):
        """Check required packages"""
        print_header("DEPENDENCY VALIDATION")
        
        required_packages = [
            'requests',
            'beautifulsoup4',
            'streamlit',
            'plotly',
            'pandas',
            'numpy',
            'openai',
            'yfinance',
            'python-dotenv',
            'aiohttp',
            'html2text',
            'chardet',
            'reportlab',
            'fpdf2'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print_success(f"{package} installed")
            except ImportError:
                print_error(f"{package} not installed")
                self.errors.append(f"Missing package: {package}")
    
    def validate_file_structure(self):
        """Check project structure"""
        print_header("FILE STRUCTURE VALIDATION")
        
        required_files = [
            'app.py',
            'orchestrator.py',
            'requirements.txt',
            'tools/ade_extractor.py',
            'tools/sec_fetcher.py',
            'tools/market_data.py',
            'tools/ratio_calculator.py',
            'tools/peer_comparator.py',
            'agents/analyst_agent.py',
            'agents/governance_agent.py',
            'agents/thesis_generator.py'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                print_success(f"{file} exists")
            else:
                print_error(f"{file} missing")
                self.errors.append(f"Missing file: {file}")
        
        # Check directories
        dirs = ['tools', 'agents', 'data/cache']
        for dir_path in dirs:
            if os.path.isdir(dir_path):
                print_success(f"{dir_path}/ directory exists")
            else:
                print_warning(f"{dir_path}/ directory missing - creating")
                os.makedirs(dir_path, exist_ok=True)
    
    def validate_imports(self):
        """Test imports of all modules"""
        print_header("MODULE IMPORT VALIDATION")
        
        try:
            # Test tool imports
            from tools.ade_extractor import LandingAIDirectExtractor
            print_success("LandingAI extractor imports successfully")
            
            from tools.sec_fetcher import SECFetcher
            print_success("SEC fetcher imports successfully")
            
            from tools.market_data import MarketDataFetcher
            print_success("Market data fetcher imports successfully")
            
            from tools.ratio_calculator import RatioCalculator
            print_success("Ratio calculator imports successfully")
            
            from tools.peer_comparator import PeerComparator
            print_success("Peer comparator imports successfully")
            
            # Test agent imports
            from agents.analyst_agent import FinancialAnalystAgent
            print_success("Financial analyst agent imports successfully")
            
            from agents.governance_agent import GovernanceAnalystAgent
            print_success("Governance analyst agent imports successfully")
            
            from agents.thesis_generator import ThesisGeneratorAgent
            print_success("Thesis generator agent imports successfully")
            
            # Test orchestrator
            from orchestrator import ActivistIntelOrchestrator
            print_success("Orchestrator imports successfully")
            
        except ImportError as e:
            print_error(f"Import failed: {str(e)}")
            self.errors.append(f"Import error: {str(e)}")
    
    async def validate_functionality(self):
        """Test basic functionality"""
        print_header("FUNCTIONALITY VALIDATION")
        
        try:
            # Test LandingAI extractor with demo mode
            from tools.ade_extractor import LandingAIDirectExtractor
            
            extractor = LandingAIDirectExtractor(api_key=None)  # Demo mode
            print_info("Testing LandingAI extractor in demo mode...")
            
            test_filings = {
                '10-K': [{'path': 'dummy.html', 'date': '2023-10-27'}]
            }
            
            result = await extractor.process_all_documents(test_filings)
            
            if result and '10k' in result:
                print_success("LandingAI extractor works in demo mode")
                print_info(f"  Sample data keys: {list(result.get('10k', {}).keys())[:5]}...")
            else:
                print_error("LandingAI extractor demo mode failed")
                self.errors.append("Demo mode extraction failed")
            
            # Test market data fetcher
            from tools.market_data import MarketDataFetcher
            
            print_info(f"Testing market data fetcher with {self.test_ticker}...")
            fetcher = MarketDataFetcher()
            data = fetcher.get_market_data(self.test_ticker)
            
            if data and data.get('market_cap', 0) > 0:
                print_success("Market data fetcher works")
                print_info(f"  {self.test_ticker} Market Cap: ${data['market_cap']/1e9:.1f}B")
            else:
                print_warning("Market data fetcher returned no data (may need internet)")
                self.warnings.append("Market data fetch failed")
            
            # Test ratio calculator
            from tools.ratio_calculator import RatioCalculator
            
            print_info("Testing ratio calculator...")
            calc = RatioCalculator()
            
            # Use data from the market data test if available, otherwise use generic test data
            if data and data.get('market_cap', 0) > 0:
                # Use real market cap from previous test
                market_cap = data['market_cap']
                print_info(f"  Using real market data from {self.test_ticker}")
            else:
                # Fallback to generic test values
                market_cap = 1000000000000  # 1 trillion
                print_info(f"  Using generic test data")
            
            test_data = {
                '10k': {
                    'revenue_current': 100000000000,     # 100B
                    'net_income_current': 20000000000,   # 20B
                    'total_assets': 150000000000,        # 150B
                    'shareholders_equity': 50000000000,  # 50B
                    'operating_income': 25000000000,     # 25B
                    'total_debt': 30000000000,           # 30B
                    'cash_equivalents': 20000000000,     # 20B
                    'revenue_prior_1': 95000000000       # 95B
                },
                'market_data': {
                    'market_cap': market_cap
                }
            }
            
            metrics = calc.calculate_all_ratios(test_data)
            
            if metrics and metrics.roe > 0:
                print_success("Ratio calculator works")
                print_info(f"  Calculated ROE: {metrics.roe:.1f}%")
                print_info(f"  Calculated ROIC: {metrics.roic:.1f}%")
            else:
                print_error("Ratio calculator failed")
                self.errors.append("Ratio calculation failed")
            
        except Exception as e:
            print_error(f"Functionality test failed: {str(e)}")
            self.errors.append(f"Functionality error: {str(e)}")
    
    def generate_report(self):
        """Generate final validation report"""
        print_header("VALIDATION SUMMARY")
        
        total_tests = len(self.successes) + len(self.warnings) + len(self.errors)
        
        print(f"\n{Fore.CYAN}Total Tests Run: {total_tests}")
        print(f"{Fore.GREEN}Passed: {len(self.successes)}")
        print(f"{Fore.YELLOW}Warnings: {len(self.warnings)}")
        print(f"{Fore.RED}Failed: {len(self.errors)}")
        
        if self.errors:
            print(f"\n{Fore.RED}CRITICAL ISSUES TO FIX:")
            for error in self.errors:
                print(f"  • {error}")
            
            print(f"\n{Fore.RED}System is NOT ready for hackathon demo!")
            return False
        
        if self.warnings:
            print(f"\n{Fore.YELLOW}WARNINGS (non-critical):")
            for warning in self.warnings:
                print(f"  • {warning}")
            
            print(f"\n{Fore.YELLOW}System will work in DEMO MODE")
        
        print(f"\n{Fore.GREEN}✅ SYSTEM READY FOR HACKATHON!")
        print(f"{Fore.GREEN}All critical components validated successfully.")
        
        return True

async def main():
    print(f"{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     SHAREHOLDER CATALYST - SYSTEM VALIDATION SUITE       ║")
    print("║           LandingAI Hackathon Production Check           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Check if ticker provided as argument
    test_ticker = 'AAPL'  # Default ticker
    if len(sys.argv) > 1:
        test_ticker = sys.argv[1].upper()
        print(f"\n{Fore.CYAN}Testing with ticker: {test_ticker}{Style.RESET_ALL}\n")
    
    validator = SystemValidator()
    validator.test_ticker = test_ticker  # Pass ticker to validator
    
    # Run all validations
    validator.validate_environment()
    validator.validate_dependencies()
    validator.validate_file_structure()
    validator.validate_imports()
    await validator.validate_functionality()
    
    # Generate report
    success = validator.generate_report()
    
    if success:
        print(f"\n{Fore.GREEN}🚀 Ready to run:")
        print(f"{Fore.CYAN}  streamlit run app.py")
        print(f"{Fore.CYAN}  python orchestrator.py {test_ticker}")
        print(f"\n{Fore.GREEN}💡 Test with different ticker:")
        print(f"{Fore.CYAN}  python test_setup.py NVDA")
        print(f"{Fore.CYAN}  python test_setup.py TSLA")
    else:
        print(f"\n{Fore.RED}⚠️  Fix the issues above before running the demo")
        print(f"{Fore.YELLOW}Install missing packages:")
        print(f"{Fore.CYAN}  pip install -r requirements.txt")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Validation interrupted by user")
        sys.exit(1)
