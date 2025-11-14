"""
Test script to verify HTML to markdown conversion
"""

import os
import tempfile
from ade_extractor_sdk import LandingAISDKExtractor

def test_html_conversion():
    """Test the HTML to markdown conversion"""
    
    # Create a sample HTML file
    sample_html = """
    <html>
    <head><title>Test 10-K</title></head>
    <body>
        <h1>Financial Statements</h1>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Revenue</td><td>$1,000,000</td></tr>
            <tr><td>Net Income</td><td>$150,000</td></tr>
        </table>
        <p>This is a test document for the conversion process.</p>
    </body>
    </html>
    """
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(sample_html)
        html_path = f.name
    
    try:
        print("Testing HTML to Markdown Conversion")
        print("=" * 50)
        
        # Initialize extractor (without API key for conversion test)
        extractor = LandingAISDKExtractor(api_key=None)
        
        # Test conversion
        print(f"\n1. Converting HTML file: {html_path}")
        md_path = extractor._html_to_markdown(html_path)
        
        if md_path:
            print(f"   ✅ Successfully converted to: {md_path}")
            
            # Read and display the markdown
            with open(md_path, 'r') as f:
                markdown_content = f.read()
            
            print(f"\n2. Markdown output ({len(markdown_content)} chars):")
            print("-" * 50)
            print(markdown_content[:500])  # First 500 chars
            print("-" * 50)
            
            print(f"\n✅ Test passed! HTML conversion works.")
            
            # Clean up
            os.unlink(md_path)
        else:
            print("   ❌ Conversion failed")
            print("\n   Please install dependencies:")
            print("   pip install beautifulsoup4 html2text")
    
    finally:
        # Clean up HTML file
        os.unlink(html_path)

if __name__ == "__main__":
    test_html_conversion()
