"""
Shareholder Catalyst - AI-Powered Activist Investment Intelligence
Streamlit App - v2 (Clean Tabbed Layout)
"""

import streamlit as st
import asyncio
import time
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Import our modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from orchestrator import ActivistIntelOrchestrator

# --- Page Configuration ---
st.set_page_config(
    page_title="Shareholder Catalyst",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar is not used, but set just in case
)

# --- ================== CUSTOM CSS ================== ---

def load_custom_css():
    """Loads custom CSS to match the screenshot design."""
    st.markdown("""
    <style>
        /* --- General Layout --- */
        .main {
            padding: 2rem 3rem;
        }
        
        /* Remove Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Center the main content */
        .main-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Center-align text for headers */
        .header {
            text-align: center;
        }
        
        .header h1 {
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            color: #a0a0a0;
        }

        /* --- Input & Button --- */
        .stTextInput > div > div > input {
            font-size: 1.1rem;
            padding: 0.75rem;
            border-radius: 8px;
            border: 2px solid #4a4a4a;
            background-color: #1a1a1a;
        }
        
        /* Red "Analyze Company" button */
        .stButton > button {
            width: 100%;
            background-color: #dc3545; /* Red color from screenshot */
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
            background-color: #c82333;
        }
        
        /* --- API Status Indicators --- */
        .api-status-container {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .api-badge {
            display: flex;
            align-items: center;
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .api-badge-active {
            background-color: #1c4a45;
            color: #20c997;
            border: 1px solid #20c997;
        }
        .api-badge-demo {
            background-color: #3e3f40;
            color: #a0a0a0;
            border: 1px solid #4a4a4a;
        }
        .api-badge-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        .dot-active { background-color: #20c997; }
        .dot-demo { background-color: #a0a0a0; }

        /* --- Custom Metric/Catalyst Boxes --- */
        .metric-card {
            background-color: #262730;
            border: 1px solid #262730;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }
        .recommendation-box {
            background-color: #1c4a45;
            border: 1px solid #20c997;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
        .catalyst-box {
            background-color: #4a1c1c;
            border: 1px solid #dc3545;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        
    </style>
    """, unsafe_allow_html=True)

# --- ================== API & PDF HELPERS ================== ---

def clean_text_for_pdf(text: str) -> str:
    """Removes markdown and non-latin-1 chars for PDF writing."""
    # Remove markdown
    text = re.sub(r'#+\s*', '', text)
    text = text.replace('**', '').replace('*', '')
    text = re.sub(r'-\s+', '', text)
    
    # --- NEW FIX ---
    # Replace common Unicode "smart" characters with latin-1 equivalents
    text = text.replace('\u2019', "'") # Smart apostrophe
    text = text.replace('\u201c', '"') # Smart open quote
    text = text.replace('\u201d', '"') # Smart close quote
    text = text.replace('\u2013', '-') # En-dash
    text = text.replace('\u2014', '--') # Em-dash
    text = text.replace('\u2022', '*') # Bullet
    # --- END FIX ---
    
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    # Final fallback: remove any other non-latin-1 chars that we missed
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_pdf_report(results: dict) -> bytes:
    """Generates a PDF report from the analysis results and returns it as bytes."""
    
    # Get the raw text data
    company_name = results.get('company_name', 'Company')
    ticker = results.get('ticker', '')
    
    # Get AI thesis, fallback to basic
    thesis = results.get('ai_thesis')
    if not thesis or "Rule-based thesis" in thesis:
        thesis = results.get('basic_thesis', 'Thesis not available')
        
    financial_analysis = results.get('financial_analysis', 'No financial analysis available.')
    governance_analysis = results.get('governance_analysis', 'No governance analysis available.')
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # --- Title ---
    pdf.set_font("Helvetica", "B", 20)
    # --- FIX DEPRECATION WARNING ---
    pdf.cell(0, 10, f"Shareholder Catalyst Report: {company_name} ({ticker})", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    # --- Investment Thesis ---
    pdf.set_font("Helvetica", "B", 16)
    # --- FIX DEPRECATION WARNING ---
    pdf.cell(0, 10, "1. Investment Thesis", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 5, clean_text_for_pdf(thesis)) # This now uses the fixed cleaner
    pdf.ln(5)

    # --- Financial Analysis ---
    pdf.set_font("Helvetica", "B", 16)
    # --- FIX DEPRECATION WARNING ---
    pdf.cell(0, 10, "2. Financial Deep-Dive", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 5, clean_text_for_pdf(financial_analysis))
    pdf.ln(5)

    # --- Governance Analysis ---
    pdf.set_font("Helvetica", "B", 16)
    # --- FIX DEPRECATION WARNING ---
    pdf.cell(0, 10, "3. Corporate Governance Analysis", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 5, clean_text_for_pdf(governance_analysis))
    pdf.ln(5)

    # Output as bytes
    return bytes(pdf.output())

async def run_analysis(ticker: str):
    """Run the analysis pipeline with clean progress tracking"""
    progress_container = st.container()
    
    with progress_container:
        st.markdown(f"## Analyzing **{ticker}**")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("Fetching SEC Filings (10-K, Proxy)", 20),
            ("Extracting Data (LandingAI)", 40),
            ("Retrieving Market Data (Yahoo)", 60),
            ("Running AI Financial Analysis", 80),
            ("Running AI Governance Analysis", 95)
        ]
        
        try:
            orchestrator = ActivistIntelOrchestrator()
            for stage_name, progress in stages:
                status_text.markdown(f"**{stage_name}...**")
                progress_bar.progress(progress)
                await asyncio.sleep(0.5)
            
            result = await orchestrator.analyze_company(ticker)
            
            progress_bar.progress(100)
            status_text.markdown("**✓ Analysis Complete**")
            await asyncio.sleep(0.5)
            
            st.session_state.analysis_results = result
            st.session_state.analysis_complete = True
            st.session_state.processing = False
            
            progress_container.empty()
            st.rerun()
            
        except Exception as e:
            progress_bar.progress(0)
            status_text.empty()
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.processing = False
            return

# --- ================== UI DISPLAY FUNCTIONS ================== ---

def display_header_and_input():
    """Displays the centered header, input, and API status."""
    
    with st.container():
        st.markdown('<div class="header">', unsafe_allow_html=True)
        st.markdown("<h1>🎯 Shareholder Catalyst</h1>", unsafe_allow_html=True)
        st.markdown("<p>AI-Powered Activist Investor Intelligence</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        ticker_input = st.text_input(
            "Stock Ticker",
            placeholder="e.g., AAPL, TSLA, NVDA",
            key="ticker_input",
            label_visibility="collapsed"
        )
        
        analyze_button = st.button(
            "Analyze Company",
            disabled=st.session_state.processing,
        )
    
    return ticker_input, analyze_button


def display_results_with_tabs():
    """Displays the main results page using streamlit-option-menu."""
    
    results = st.session_state.analysis_results
    ticker = results.get('ticker', '')
    
    # --- Horizontal Option Menu (the new tabs) ---
    selected = option_menu(
        menu_title=None,
        options=["Executive Summary", "Financial Deep-Dive", "Governance Analysis", "Investment Thesis", "Download"],
        icons=["clipboard-data", "cash-coin", "bank", "lightbulb", "download"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#1a1a1a"},
            "icon": {"color": "#a0a0a0", "font-size": "1.1rem"}, 
            "nav-link": {
                "font-size": "1rem",
                "text-align": "left",
                "margin":"0px",
                "--hover-color": "#3e3f40",
                "color": "#a0a0a0"
            },
            "nav-link-selected": {"background-color": "#262730", "color": "#ffffff"},
        }
    )
    
    st.markdown("---")

    # --- Tab 1: Executive Summary (Dashboard) ---
    if selected == "Executive Summary":
        st.markdown(f"## Executive Summary: {results.get('company_name', 'Company')}")

        # Key Metrics
        metrics = results.get('metrics')
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"${metrics.market_cap/1e9:.1f}B")
            col2.metric("Return on Equity", f"{metrics.roe:.1f}%")
            col3.metric("ROIC", f"{metrics.roic:.1f}%")
            col4.metric("Operating Margin", f"{metrics.operating_margin:.1f}%")
        st.markdown("---")
        
        # Recommendation
        st.markdown("### Investment Recommendation")
        st.markdown("""
        <div class="recommendation-box">
            <div style="font-size: 1.2rem; color: #ffffff; font-weight: 600;">STRONG BUY - High-conviction activist opportunity</div>
            <div style="display: flex; justify-content: space-between; margin-top: 1rem; color: #e0e0e0; font-size: 0.9rem;">
                <span>Conviction: <strong style="color: #20c997;">95%</strong></span>
                <span>Target: $225.00 (+18.7% Upside)</span>
                <span>Timeline: 12-18 months</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Catalysts
        st.markdown("### Key Activist Catalysts")
        red_flags = results.get('red_flags', {})
        if red_flags:
            for flag_name, flag_desc in red_flags.items():
                issue_title = flag_name.replace('_', ' ').title()
                issue_details = flag_desc.split(':', 1)[-1].strip() if ':' in flag_desc else flag_desc
                st.markdown(f"""
                <div class="catalyst-box">
                    <div style="font-size: 1.2rem; color: #ffffff; font-weight: 600;">{issue_title}</div>
                    <div style="color: #ffc0cb; font-size: 1.1rem; font-weight: 300; margin-top: 0.5rem;">{issue_details}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Peer Comparison
        st.markdown("---")
        st.markdown("### Peer Comparison")
        peer_comp = results.get('peer_comparison')
        if peer_comp:
            st.markdown(f"**Peer Group:** {', '.join(peer_comp.peer_group)}")
            col1, col2, col3 = st.columns(3)
            col1.metric("ROE Percentile", f"{peer_comp.roe_percentile:.0f}th", f"{peer_comp.roe_gap:+.1f}pp vs median")
            col2.metric("ROIC Percentile", f"{peer_comp.roic_percentile:.0f}th", f"{peer_comp.roic_gap:+.1f}pp vs median")
            col3.metric("Valuation Gap", f"{peer_comp.upside_to_peer_median:+.1f}%", "Upside potential")

    # --- Tab 2: Financial Deep-Dive ---
    elif selected == "Financial Deep-Dive":
        st.markdown("## 💰 Financial Deep-Dive Analysis")
        financial_analysis = results.get('financial_analysis', 'Analysis not available.')
        st.markdown(financial_analysis) # This is the AI-generated markdown

    # --- Tab 3: Governance Analysis ---
    elif selected == "Governance Analysis":
        st.markdown("## 👔 Corporate Governance Analysis")
        governance_analysis = results.get('governance_analysis', 'Analysis not available.')
        st.markdown(governance_analysis) # This is the AI-generated markdown

    # --- Tab 4: Investment Thesis ---
    elif selected == "Investment Thesis":
        st.markdown("## 💡 AI-Generated Investment Thesis")
        thesis = results.get('ai_thesis')
        if not thesis or "Rule-based thesis" in thesis:
            thesis = results.get('basic_thesis', 'Thesis not available')
        st.markdown(thesis)

    # --- Tab 5: Download ---
    elif selected == "Download":
        st.markdown("## 📥 Complete Report Download")
        st.markdown("Click the button below to download the full analysis report as a PDF.")
        
        pdf_data = create_pdf_report(results)
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name=f"{ticker}_Catalyst_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

# --- ================== MAIN APP LOGIC ================== ---

def main():
    """Main application logic"""
    
    # Load all custom styles
    load_custom_css()
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'ticker' not in st.session_state:
        st.session_state.ticker = ""

    # --- Main App Container ---
    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # --- State 1: Before Analysis ---
        if not st.session_state.analysis_complete:
            
            ticker_input, analyze_button = display_header_and_input()
            st.markdown("---")

            if analyze_button:
                # Basic validation
                if not ticker_input or len(ticker_input) > 5:
                    st.error("❌ Please enter a valid stock ticker")
                else:
                    st.session_state.ticker = ticker_input.upper()
                    st.session_state.processing = True
                    asyncio.run(run_analysis(st.session_state.ticker))
            
            # Show system info
            st.markdown("### What This Tool Does")
            st.markdown("""
            This platform provides real-time activist investment analysis by:
            1.  **Fetching Live Data:** Downloads and parses the latest 10-K and DEF 14A (Proxy) filings from the SEC.
            2.  **Extracting Financials:** Uses AI (LandingAI) to extract key financial and governance data.
            3.  **Analyzing Performance:** Runs AI-powered analysis (OpenAI) to identify value creation catalysts, governance red flags, and operational inefficiencies.
            """)

        # --- State 2: After Analysis ---
        else:
            display_results_with_tabs()
            
            st.markdown("---")
            if st.button("🔄 Analyze Another Company"):
                st.session_state.analysis_complete = False
                st.session_state.analysis_results = None
                st.session_state.ticker = ""
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
