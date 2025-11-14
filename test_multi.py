#!/usr/bin/env python3
"""
Shareholder Catalyst - Comprehensive Testing Suite
Tests system with multiple tickers and validates real-time data
"""

import os
import sys
import asyncio
from datetime import datetime

# Add color support
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        GREEN = RED = YELLOW = CYAN = BLUE = ""
    class Style:
        RESET_ALL = ""

def print_header(text):
    print(f"\n{Fore.BLUE}{'='*70}")
    print(f"{Fore.BLUE}{text}")
    print(f"{Fore.BLUE}{'='*70}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.CYAN}ℹ️  {text}{Style.RESET_ALL}")

async def test_ticker(ticker: str):
    """Test analysis with a specific ticker"""
    
    print_header(f"Testing: {ticker}")
    
    results = {
        'ticker': ticker,
        'sec_success': False,
        'market_success': False,
        'extraction_success': False,
        'analysis_success': False,
        'errors': []
    }
    
    try:
        # Test SEC Fetcher
        print_info(f"1. Testing SEC filing retrieval for {ticker}...")
        from tools.sec_fetcher import SECFetcher
        
        fetcher = SECFetcher(ticker)
        cik = fetcher._get_cik()
        
        if cik and fetcher.company_name:
            print_success(f"SEC: Found {fetcher.company_name} (CIK: {cik})")
            results['sec_success'] = True
            results['company_name'] = fetcher.company_name
        else:
            print_error(f"SEC: Could not find ticker {ticker}")
            results['errors'].append("SEC lookup failed")
        
    except Exception as e:
        print_error(f"SEC Error: {str(e)}")
        results['errors'].append(f"SEC: {str(e)}")
    
    try:
        # Test Market Data
        print_info(f"2. Testing market data retrieval for {ticker}...")
        from tools.market_data import MarketDataFetcher
        
        market_fetcher = MarketDataFetcher()
        market_data = market_fetcher.get_market_data(ticker)
        
        if market_data and market_data.get('market_cap', 0) > 0:
            print_success(f"Market: Cap=${market_data['market_cap']/1e9:.1f}B, Price=${market_data['current_price']:.2f}")
            results['market_success'] = True
            results['market_cap'] = market_data['market_cap']
            results['price'] = market_data['current_price']
        else:
            print_warning(f"Market: Data not available for {ticker}")
            results['errors'].append("Market data unavailable")
        
    except Exception as e:
        print_error(f"Market Error: {str(e)}")
        results['errors'].append(f"Market: {str(e)}")
    
    try:
        # Test Extraction (demo mode)
        print_info(f"3. Testing document extraction (demo mode)...")
        from tools.ade_extractor import LandingAIDirectExtractor
        
        extractor = LandingAIDirectExtractor(api_key=None)  # Demo mode
        test_filings = {
            '10-K': [{'path': f'test_{ticker}_10k.html', 'date': '2023-10-27'}]
        }
        
        extracted = await extractor.process_all_documents(test_filings)
        
        if extracted and '10k' in extracted:
            print_success(f"Extraction: Demo data available")
            results['extraction_success'] = True
        else:
            print_warning(f"Extraction: Demo data not complete")
        
    except Exception as e:
        print_error(f"Extraction Error: {str(e)}")
        results['errors'].append(f"Extraction: {str(e)}")
    
    # Calculate score
    total_tests = 3  # SEC, Market, Extraction
    passed = sum([results['sec_success'], results['market_success'], results['extraction_success']])
    results['score'] = f"{passed}/{total_tests}"
    results['percentage'] = int((passed / total_tests) * 100)
    
    return results

async def main():
    """Main test runner"""
    
    print(f"{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   SHAREHOLDER CATALYST - MULTI-TICKER VALIDATION SUITE       ║")
    print("║         Test real-time data with multiple companies         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Get tickers from command line or use defaults
    if len(sys.argv) > 1:
        tickers = [t.upper().strip() for t in sys.argv[1:]]
        print_info(f"Testing with provided tickers: {', '.join(tickers)}\n")
    else:
        tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA']
        print_info(f"Testing with default tickers: {', '.join(tickers)}")
        print_info(f"To test specific tickers: python test_multi.py TICKER1 TICKER2 ...\n")
    
    # Run tests for each ticker
    all_results = []
    
    for ticker in tickers:
        result = await test_ticker(ticker)
        all_results.append(result)
        
        # Brief pause between tests
        await asyncio.sleep(1)
    
    # Generate summary report
    print_header("TEST SUMMARY")
    
    print(f"\n{Fore.CYAN}┌─────────────┬───────────────────────────┬───────┬──────────┐")
    print(f"│ {'Ticker':<11} │ {'Company':<25} │ Score │ Status   │")
    print(f"├─────────────┼───────────────────────────┼───────┼──────────┤{Style.RESET_ALL}")
    
    success_count = 0
    
    for result in all_results:
        ticker = result['ticker']
        company = result.get('company_name', 'Unknown')[:25]
        score = result['score']
        percentage = result['percentage']
        
        # Determine status color
        if percentage >= 67:
            status_color = Fore.GREEN
            status = "✅ PASS"
            success_count += 1
        elif percentage >= 33:
            status_color = Fore.YELLOW
            status = "⚠️  PARTIAL"
        else:
            status_color = Fore.RED
            status = "❌ FAIL"
        
        print(f"{Fore.CYAN}│ {ticker:<11} │ {company:<25} │ {score:<5} │ {status_color}{status}{Fore.CYAN}  │{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}└─────────────┴───────────────────────────┴───────┴──────────┘{Style.RESET_ALL}")
    
    # Overall statistics
    print(f"\n{Fore.CYAN}Overall Statistics:")
    print(f"  Tickers Tested: {len(all_results)}")
    print(f"  Passed: {Fore.GREEN}{success_count}{Fore.CYAN}")
    print(f"  Failed: {Fore.RED}{len(all_results) - success_count}{Style.RESET_ALL}")
    
    # Show any errors
    errors_found = False
    for result in all_results:
        if result['errors']:
            if not errors_found:
                print_header("ERRORS DETAILS")
                errors_found = True
            print(f"\n{Fore.RED}{result['ticker']}:{Style.RESET_ALL}")
            for error in result['errors']:
                print(f"  • {error}")
    
    # Success criteria
    print_header("VERDICT")
    
    success_rate = (success_count / len(all_results)) * 100
    
    if success_rate >= 75:
        print(f"{Fore.GREEN}✅ SYSTEM READY FOR PRODUCTION")
        print(f"   {success_rate:.0f}% of tickers passed validation")
        print(f"\n🚀 Ready to analyze ANY public company!")
        print(f"\nQuick Start:")
        print(f"  streamlit run app.py")
        return True
    elif success_rate >= 50:
        print(f"{Fore.YELLOW}⚠️  SYSTEM PARTIALLY FUNCTIONAL")
        print(f"   {success_rate:.0f}% of tickers passed validation")
        print(f"\n💡 App will work but some features may be limited")
        print(f"   Check errors above and verify internet connectivity")
        return True
    else:
        print(f"{Fore.RED}❌ SYSTEM NEEDS ATTENTION")
        print(f"   Only {success_rate:.0f}% of tickers passed validation")
        print(f"\n🔧 Please fix the errors above before running")
        return False

if __name__ == "__main__":
    try:
        print(f"\n{Fore.YELLOW}Starting validation at {datetime.now().strftime('%H:%M:%S')}...{Style.RESET_ALL}\n")
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Validation interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
