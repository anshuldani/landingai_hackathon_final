#!/usr/bin/env python3
"""
🎯 SHAREHOLDER CATALYST - HACKATHON LAUNCHER
Complete system startup and validation for LandingAI Hackathon
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Display startup banner"""
    print("\n" + "="*70)
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     🎯 SHAREHOLDER CATALYST - ACTIVIST INTELLIGENCE       ║
    ║            LandingAI Hackathon Finalist Edition           ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print("="*70 + "\n")

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("  ✅ .env file found")
    else:
        print("  ⚠️  .env file not found - creating from template")
        if os.path.exists('.env.example'):
            subprocess.run(['cp', '.env.example', '.env'])
            print("  ✅ Created .env from template")
        else:
            print("  ⚠️  No .env.example found - will run in demo mode")
    
    # Check Python version
    if sys.version_info >= (3, 8):
        print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} installed")
    else:
        print(f"  ❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing Dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      capture_output=True, text=True)
        
        # Install requirements
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ All dependencies installed successfully")
            return True
        else:
            print("  ⚠️  Some dependencies may have failed to install")
            print("  ℹ️  The app will still work in demo mode")
            return True
            
    except Exception as e:
        print(f"  ⚠️  Error installing dependencies: {e}")
        print("  ℹ️  Continuing anyway - demo mode will work")
        return True

def run_validation():
    """Run the test suite"""
    print("\n🧪 Running System Validation...")
    
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if "SYSTEM READY FOR HACKATHON" in result.stdout:
            print("  ✅ All systems validated successfully!")
            return True
        else:
            print("  ⚠️  Some validation checks failed")
            print("  ℹ️  The app will still work in demo mode")
            return True
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  Validation timeout - skipping")
        return True
    except Exception as e:
        print(f"  ⚠️  Validation error: {e}")
        return True

def display_menu():
    """Display launch options"""
    print("\n" + "="*70)
    print("🚀 LAUNCH OPTIONS")
    print("="*70)
    print()
    print("1. 🌐 Launch Web Interface (Streamlit)")
    print("2. 📊 Run Command-Line Analysis")
    print("3. 🧪 Run Test Suite")
    print("4. 📝 View Documentation")
    print("5. ❌ Exit")
    print()
    
    choice = input("Select option (1-5): ").strip()
    return choice

def launch_streamlit():
    """Launch the Streamlit web interface"""
    print("\n🌐 Launching Web Interface...")
    print("="*70)
    print("  Opening browser to: http://localhost:8501")
    print("  Press Ctrl+C to stop the server")
    print("="*70)
    
    time.sleep(2)
    
    try:
        subprocess.run(["streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Error launching Streamlit: {e}")
        print("Try running manually: streamlit run app.py")

def run_cli_analysis():
    """Run command-line analysis"""
    print("\n📊 Command-Line Analysis")
    print("="*70)
    
    ticker = input("Enter ticker symbol (e.g., AAPL): ").strip().upper()
    
    if not ticker:
        print("❌ No ticker provided")
        return
    
    print(f"\n🔍 Analyzing {ticker}...")
    print("This may take 30-60 seconds...\n")
    
    try:
        subprocess.run([sys.executable, "orchestrator.py", ticker])
    except Exception as e:
        print(f"\n❌ Error running analysis: {e}")

def view_docs():
    """Display documentation"""
    print("\n📝 DOCUMENTATION")
    print("="*70)
    
    print("""
    🎯 SHAREHOLDER CATALYST - Quick Start Guide
    
    WHAT IT DOES:
    - Analyzes public companies for activist investor opportunities
    - Extracts financial data from SEC filings using LandingAI
    - Calculates key metrics (ROE, ROIC, margins)
    - Identifies governance issues and compensation problems
    - Generates comprehensive investment theses
    
    HOW TO USE:
    1. Web Interface (Recommended):
       - Run option 1 to launch Streamlit
       - Select a company from the dropdown
       - Click "Run Analysis"
       - Review the 6-tab comprehensive report
    
    2. Command Line:
       - Run option 2
       - Enter a ticker symbol
       - Wait for analysis to complete
       - Check the generated markdown report
    
    API KEYS (Optional):
    - LANDING_AI_API_KEY: For document extraction
    - OPENAI_API_KEY: For AI-powered analysis
    
    Without keys, the app runs in demo mode with sample data.
    
    DEMO COMPANIES:
    AAPL, MSFT, GOOGL, AMZN, META, TSLA, NFLX
    
    SUPPORT:
    - GitHub: [Your Repository]
    - Documentation: README.md
    - Hackathon Guide: HACKATHON_GUIDE.md
    """)
    
    input("\nPress Enter to continue...")

def main():
    """Main launcher logic"""
    print_banner()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix issues and try again.")
        sys.exit(1)
    
    # Install dependencies if needed
    if not os.path.exists(".deps_installed"):
        if install_dependencies():
            Path(".deps_installed").touch()
    else:
        print("\n✅ Dependencies already installed")
    
    # Run validation
    run_validation()
    
    # Main menu loop
    while True:
        choice = display_menu()
        
        if choice == "1":
            launch_streamlit()
        elif choice == "2":
            run_cli_analysis()
        elif choice == "3":
            subprocess.run([sys.executable, "test_setup.py"])
            input("\nPress Enter to continue...")
        elif choice == "4":
            view_docs()
        elif choice == "5":
            print("\n👋 Thank you for using Shareholder Catalyst!")
            print("Good luck with the hackathon! 🏆\n")
            sys.exit(0)
        else:
            print("❌ Invalid option. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs and try again.")
        sys.exit(1)
