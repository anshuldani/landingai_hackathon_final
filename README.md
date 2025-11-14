# 🎯 Shareholder Catalyst - Real-Time Activist Intelligence Platform

AI-powered platform for identifying activist investment opportunities in public companies using real-time SEC filings and market data.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional but Recommended)

Create a `.env` file in the project root:

```bash
# For document extraction (LandingAI)
LANDING_AI_API_KEY=your_landingai_api_key_here

# For AI-powered analysis (OpenAI)
OPENAI_API_KEY=your_openai_api_key_here
```

**Note:** The app works WITHOUT API keys using:
- ✅ Real SEC filings from EDGAR
- ✅ Real-time market data from Yahoo Finance
- ⚠️ Limited sample extraction data (2 companies)

### 3. Launch the App

```bash
streamlit run app.py
```

Or use the interactive launcher:

```bash
python run.py
```

## 📊 Features

### Real-Time Data Sources
- **SEC EDGAR Filings** - Downloads actual 10-K, Proxy, and 8-K filings
- **Yahoo Finance** - Real-time market prices, market cap, P/E ratios
- **LandingAI Document Extraction** - Extracts financial data from filings (requires API key)
- **OpenAI GPT-4 Analysis** - AI-powered investment thesis generation (requires API key)

### Analysis Capabilities
- Financial performance metrics (ROE, ROIC, margins)
- Governance analysis (board composition, compensation)
- Peer benchmarking
- Value creation opportunities identification
- Investment thesis generation

## 🔧 Troubleshooting

### Common Issues

#### 1. **"ModuleNotFoundError" or Import Errors**

```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# If still failing, try installing individually
pip install streamlit plotly pandas yfinance beautifulsoup4 openai python-dotenv
```

#### 2. **SEC Fetcher Errors**

**Problem:** `Ticker {TICKER} not found in SEC database`

**Solution:**
- Verify the ticker symbol is correct (must be a U.S. public company)
- Check that the company files with the SEC
- Try major tickers first (AAPL, MSFT, GOOGL, TSLA)

**Problem:** `Connection timeout or refused`

**Solution:**
```bash
# Test SEC connection
python -c "import requests; r=requests.get('https://www.sec.gov/files/company_tickers.json', headers={'User-Agent': 'test@test.com'}); print(r.status_code)"
```

If this fails, check your internet connection or firewall settings.

#### 3. **Market Data Issues**

**Problem:** `Error fetching market data`

**Solution:**
- Yahoo Finance may be temporarily down
- Check internet connection
- Try a well-known ticker (AAPL) first
- The app will continue with estimated data if this fails

#### 4. **LandingAI API Errors**

**Problem:** `401 Unauthorized` or `Invalid API key`

**Solution:**
- Verify your API key in `.env` file
- Check for extra spaces or quotes around the key
- Ensure key has sufficient credits
- App will work in demo mode without the key

**Problem:** `Rate limit exceeded`

**Solution:**
- Wait a few minutes and try again
- LandingAI has rate limits on API calls
- Consider upgrading your API plan

#### 5. **Streamlit App Not Loading**

**Problem:** Browser shows "Please wait..." indefinitely

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart with fresh session
streamlit run app.py --server.port 8502
```

#### 6. **Analysis Hangs or Takes Too Long**

**Problem:** Analysis stuck on "Fetching SEC Filings..."

**Solution:**
- SEC servers can be slow during peak hours
- Try a different ticker
- Check console output for actual errors
- Press Ctrl+C and restart

## 🧪 Testing Individual Components

### Test with Any Ticker

```bash
# Test with default ticker (AAPL)
python test_setup.py

# Test with specific ticker
python test_setup.py NVDA
python test_setup.py TSLA

# Test multiple tickers at once
python test_multi.py AAPL MSFT GOOGL NVDA TSLA
```

### Test Specific Components

#### Test SEC Fetcher
```bash
python -c "from tools.sec_fetcher import SECFetcher; f = SECFetcher('NVDA'); print(f._get_cik())"
```

#### Test Market Data
```bash
python tools/market_data.py
```

#### Test Full Analysis (CLI)
```bash
# Test with any ticker
python orchestrator.py NVDA
python orchestrator.py TSLA
python orchestrator.py AMZN
```

### Comprehensive Multi-Ticker Validation
```bash
# Test with multiple companies at once
python test_multi.py AAPL MSFT GOOGL NVDA TSLA META AMZN

# Quick 4-ticker test (default)
python test_multi.py
```

## 📝 API Key Setup Instructions

### Getting LandingAI API Key

1. Go to https://landing.ai
2. Sign up / Login
3. Navigate to API section
4. Generate new API key
5. Add to `.env` as `LANDING_AI_API_KEY=your_key`

### Getting OpenAI API Key

1. Go to https://platform.openai.com
2. Sign up / Login
3. Go to API Keys section
4. Create new secret key
5. Add to `.env` as `OPENAI_API_KEY=your_key`

## 🎯 Usage Examples

### Web Interface

1. Launch: `streamlit run app.py`
2. Enter any ticker symbol (e.g., NVDA, TSLA, AMZN)
3. Click "Analyze"
4. Review comprehensive analysis results

### Command Line

```bash
# Analyze any company
python orchestrator.py NVDA

# Results saved to markdown file
```

## 🔍 What Gets Analyzed

For any U.S. public company:

1. **Financial Metrics**
   - Revenue, income, margins
   - ROE, ROIC, capital efficiency
   - Cash position and debt levels

2. **Governance**
   - Board composition and independence
   - Director tenure
   - CEO compensation structure
   - Say-on-pay voting results

3. **Value Creation Opportunities**
   - Operational inefficiencies
   - Excess cash deployment
   - Margin improvement potential
   - Strategic recommendations

4. **Investment Thesis**
   - AI-generated or rule-based analysis
   - Specific activist recommendations
   - Expected value creation potential

## 🐛 Reporting Issues

If you encounter persistent errors:

1. Check console output for detailed error messages
2. Verify all dependencies are installed correctly
3. Test individual components (see Testing section above)
4. Ensure API keys are valid (if using)
5. Try with a well-known ticker (AAPL) first

## 📚 Project Structure

```
shareholder-catalyst/
├── app.py                 # Main Streamlit application
├── orchestrator.py        # Analysis pipeline coordinator
├── tools/
│   ├── sec_fetcher.py    # SEC EDGAR filing retrieval
│   ├── ade_extractor.py  # LandingAI document extraction
│   ├── market_data.py    # Yahoo Finance real-time data
│   ├── ratio_calculator.py  # Financial metrics
│   └── peer_comparator.py   # Peer benchmarking
├── agents/
│   ├── analyst_agent.py     # Financial analysis
│   ├── governance_agent.py  # Governance review
│   └── thesis_generator.py  # Investment thesis
├── requirements.txt      # Python dependencies
└── .env                 # API keys (create this)
```

## ⚡ Performance Tips

1. **First run is slower** - Downloads SEC filings and initializes models
2. **Use specific tickers** - Avoid ambiguous symbols
3. **Check API quotas** - If using LandingAI/OpenAI keys
4. **Internet required** - For SEC filings and market data

## 🔐 Security Notes

- Never commit `.env` file to git
- Keep API keys private
- API keys are read from environment variables only
- No API keys = demo mode (still works!)

## 💡 Tips for Best Results

1. **Use major public companies first** (AAPL, MSFT, etc.)
2. **Add both API keys** for full AI-powered analysis
3. **Check during market hours** for most current data
4. **Try multiple companies** to compare opportunities
5. **Export reports** for detailed review

## 🎓 How It Works

1. **Fetches real SEC filings** from EDGAR database
2. **Extracts financial data** using LandingAI or fallback parsing
3. **Gets real-time prices** from Yahoo Finance
4. **Calculates key metrics** (ROE, ROIC, margins)
5. **Benchmarks against peers** for relative performance
6. **Identifies red flags** indicating activist opportunities
7. **Generates thesis** using AI or rule-based analysis

## 📞 Support

For issues or questions:
- Check the Troubleshooting section above
- Review console output for specific errors
- Test individual components separately
- Verify ticker symbol is valid U.S. public company

---

**Made for real-time analysis of public companies using live SEC and market data** 🚀
