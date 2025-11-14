"""
Shareholder Catalyst - Minimalist Real-Time Activist Intelligence Platform
Clean, modern UI for analyzing any public company
"""

import streamlit as st
import asyncio
import time
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import ActivistIntelOrchestrator

# Page configuration
st.set_page_config(
    page_title="Shareholder Catalyst",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimalist Custom CSS
st.markdown("""
<style>
    /* Clean, modern styling */
    .main {
        padding: 2rem 3rem;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }
    
    /* Clean headers */
    h1 {
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-weight: 500;
        color: #2a2a2a;
        margin-top: 2rem;
    }
    
    h3 {
        font-weight: 500;
        color: #4a4a4a;
        font-size: 1.2rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        border-radius: 8px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-success {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .badge-warning {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'ticker' not in st.session_state:
    st.session_state.ticker = ""

def check_api_status():
    """Check API key status"""
    landing_key = os.getenv('LANDING_AI_API_KEY') or os.getenv('VISION_AGENT_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    return {
        'landing_ai': bool(landing_key),
        'openai': bool(openai_key)
    }

def display_header():
    """Display clean header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🎯 Shareholder Catalyst")
        st.markdown("**AI-Powered Activist Investment Intelligence**")
    
    with col2:
        api_status = check_api_status()
        if api_status['landing_ai'] and api_status['openai']:
            st.markdown('<span class="status-badge badge-success">● All Systems Active</span>', 
                       unsafe_allow_html=True)
        elif api_status['landing_ai'] or api_status['openai']:
            st.markdown('<span class="status-badge badge-warning">● Partial Mode</span>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-warning">● Demo Mode</span>', 
                       unsafe_allow_html=True)

def validate_ticker(ticker: str) -> tuple[bool, str]:
    """Validate ticker input"""
    ticker = ticker.strip().upper()
    
    if not ticker:
        return False, "Please enter a ticker symbol"
    
    if len(ticker) > 5:
        return False, "Ticker symbol too long (max 5 characters)"
    
    if not ticker.isalpha():
        return False, "Ticker should only contain letters"
    
    return True, ticker

async def run_analysis(ticker: str):
    """Run the analysis pipeline with clean progress tracking"""
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown(f"## Analyzing **{ticker}**")
        st.markdown("---")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stage tracking
        stages = [
            ("Fetching SEC Filings", 20),
            ("Extracting Financial Data", 40),
            ("Retrieving Market Data", 60),
            ("Analyzing Performance", 80),
            ("Generating Investment Thesis", 95)
        ]
        
        try:
            # Initialize orchestrator
            orchestrator = ActivistIntelOrchestrator()
            
            # Update progress through stages
            for stage_name, progress in stages:
                status_text.markdown(f"**{stage_name}...**")
                progress_bar.progress(progress)
                await asyncio.sleep(0.5)
            
            # Run actual analysis
            result = await orchestrator.analyze_company(ticker)
            
            # Complete
            progress_bar.progress(100)
            status_text.markdown("**✓ Analysis Complete**")
            await asyncio.sleep(0.5)
            
            # Store results
            st.session_state.analysis_results = result
            st.session_state.analysis_complete = True
            st.session_state.processing = False
            
            # Clear progress display
            progress_container.empty()
            
            # Show success message
            st.success(f"✓ Successfully analyzed {result.get('company_name', ticker)}")
            
            # Rerun to show results
            st.rerun()
            
        except Exception as e:
            progress_bar.progress(0)
            status_text.empty()
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.processing = False
            return

def display_key_metrics(results):
    """Display key metrics in clean cards"""
    st.markdown("## Key Metrics")
    
    metrics = results.get('metrics')
    if not metrics:
        st.info("Metrics data not available")
        return
    
    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Return on Equity",
            f"{metrics.roe:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "ROIC",
            f"{metrics.roic:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "Operating Margin",
            f"{metrics.operating_margin:.1f}%",
            delta=None
        )
    
    with col4:
        revenue_growth = metrics.revenue_growth_1y
        st.metric(
            "Revenue Growth",
            f"{revenue_growth:.1f}%",
            delta=f"{revenue_growth:.1f}%"
        )
    
    st.markdown("---")

def display_financial_overview(results):
    """Display financial overview"""
    st.markdown("## Financial Overview")
    
    extracted_data = results.get('extracted_data', {})
    financial_data = extracted_data.get('10k', {})
    market_data = extracted_data.get('market_data', {})
    
    if not financial_data:
        st.info("Financial data not available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Income Statement")
        revenue = financial_data.get('revenue_current', 0)
        operating_income = financial_data.get('operating_income', 0)
        net_income = financial_data.get('net_income_current', 0)
        
        st.markdown(f"**Revenue:** ${revenue/1e9:.2f}B")
        st.markdown(f"**Operating Income:** ${operating_income/1e9:.2f}B")
        st.markdown(f"**Net Income:** ${net_income/1e9:.2f}B")
    
    with col2:
        st.markdown("### Balance Sheet")
        total_assets = financial_data.get('total_assets', 0)
        cash = financial_data.get('cash_equivalents', 0)
        debt = financial_data.get('total_debt', 0)
        
        st.markdown(f"**Total Assets:** ${total_assets/1e9:.2f}B")
        st.markdown(f"**Cash:** ${cash/1e9:.2f}B")
        st.markdown(f"**Total Debt:** ${debt/1e9:.2f}B")
    
    st.markdown("---")

def display_investment_thesis(results):
    """Display investment thesis"""
    st.markdown("## Investment Thesis")
    
    # Try AI thesis first, fall back to basic
    thesis = results.get('ai_thesis')
    if not thesis or thesis == "Rule-based thesis (add LLM key for AI-generated thesis)":
        thesis = results.get('basic_thesis', 'Thesis not available')
    
    st.markdown(thesis)
    
    st.markdown("---")

def display_red_flags(results):
    """Display activist opportunities"""
    st.markdown("## Value Creation Opportunities")
    
    red_flags = results.get('red_flags', {})
    
    if red_flags:
        for flag_name, flag_desc in red_flags.items():
            with st.expander(f"⚠️ {flag_name.replace('_', ' ').title()}", expanded=True):
                st.markdown(f"**Issue:** {flag_desc}")
                st.markdown("**Recommendation:** Address through operational improvements")
    else:
        st.success("✓ No major operational inefficiencies detected")
    
    st.markdown("---")

def display_governance(results):
    """Display governance analysis"""
    st.markdown("## Governance Analysis")
    
    extracted_data = results.get('extracted_data', {})
    proxy_data = extracted_data.get('proxy', {})
    
    if not proxy_data or proxy_data.get('board_size', 0) == 0:
        st.info("Governance data not available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Board Size", proxy_data.get('board_size', 0))
    
    with col2:
        independent = proxy_data.get('independent_directors', 0)
        total = proxy_data.get('board_size', 1)
        st.metric("Independent Directors", f"{independent}/{total}")
    
    with col3:
        tenure = proxy_data.get('average_director_tenure', 0)
        st.metric("Avg. Tenure", f"{tenure:.1f} years")
    
    # CEO Compensation
    st.markdown("### CEO Compensation")
    ceo_comp = proxy_data.get('ceo_total_comp_current', 0)
    if ceo_comp > 0:
        st.markdown(f"**Total Compensation:** ${ceo_comp/1e6:.1f}M")
        
        # Breakdown
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"Base: ${proxy_data.get('ceo_base_salary', 0)/1e6:.1f}M")
        with col2:
            st.markdown(f"Bonus: ${proxy_data.get('ceo_bonus', 0)/1e6:.1f}M")
        with col3:
            st.markdown(f"Stock: ${proxy_data.get('ceo_stock_awards', 0)/1e6:.1f}M")

def display_results():
    """Display complete analysis results"""
    if not st.session_state.analysis_complete or not st.session_state.analysis_results:
        return
    
    results = st.session_state.analysis_results
    
    # Company header
    company_name = results.get('company_name', 'Company')
    ticker = results.get('ticker', '')
    
    st.markdown(f"# {company_name} ({ticker})")
    st.markdown(f"*Analysis completed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
    st.markdown("---")
    
    # Display sections
    display_key_metrics(results)
    display_financial_overview(results)
    display_investment_thesis(results)
    display_red_flags(results)
    display_governance(results)
    
    # Export option
    st.markdown("---")
    if st.button("📥 Export Full Report"):
        from orchestrator import save_results
        output_file = save_results(results)
        st.success(f"Report saved to: {output_file}")

def main():
    """Main application logic"""
    
    # Display header
    display_header()
    
    st.markdown("---")
    
    # If not showing results, show input form
    if not st.session_state.analysis_complete:
        # Input section
        st.markdown("### Analyze Any Public Company")
        st.markdown("Enter a stock ticker symbol to get comprehensive activist investment analysis")
        
        # Create two-column layout for input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ticker_input = st.text_input(
                "Stock Ticker",
                placeholder="e.g., AAPL, TSLA, NVDA",
                key="ticker_input",
                label_visibility="collapsed"
            )
        
        with col2:
            analyze_button = st.button(
                "🚀 Analyze",
                disabled=st.session_state.processing,
                type="primary"
            )
        
        # Show examples
        st.markdown("**Popular examples:** AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META")
        
        # Handle analysis trigger
        if analyze_button:
            is_valid, result = validate_ticker(ticker_input)
            
            if is_valid:
                st.session_state.ticker = result
                st.session_state.processing = True
                asyncio.run(run_analysis(result))
            else:
                st.error(f"❌ {result}")
        
        # Show system info
        st.markdown("---")
        st.markdown("### What This Tool Does")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 SEC Filing Analysis**
            - Extracts financial data
            - Analyzes governance
            - Reviews compensation
            """)
        
        with col2:
            st.markdown("""
            **📊 Performance Metrics**
            - ROE, ROIC calculations
            - Margin analysis
            - Peer comparison
            """)
        
        with col3:
            st.markdown("""
            **💡 Investment Thesis**
            - Value creation opportunities
            - Activist recommendations
            - Strategic insights
            """)
        
        # API Status info
        api_status = check_api_status()
        if not api_status['landing_ai'] or not api_status['openai']:
            st.info("""
            ℹ️ **Running in partial mode** - Add API keys to `.env` for full functionality:
            - `LANDING_AI_API_KEY` for document extraction
            - `OPENAI_API_KEY` for AI-powered analysis
            """)
    
    else:
        # Display results
        display_results()
        
        # New analysis button
        st.markdown("---")
        if st.button("🔄 Analyze Another Company", type="secondary"):
            st.session_state.analysis_complete = False
            st.session_state.analysis_results = None
            st.session_state.ticker = ""
            st.rerun()

if __name__ == "__main__":
    main()
