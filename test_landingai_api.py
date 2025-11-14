#!/usr/bin/env python3
"""
LandingAI API Test Script
Test different payload formats to find what works
"""

import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv()

# Get API key
api_key = os.getenv('LANDING_AI_API_KEY') or os.getenv('VISION_AGENT_API_KEY')

if not api_key:
    print("❌ No API key found in environment!")
    print("Set LANDING_AI_API_KEY or VISION_AGENT_API_KEY in .env file")
    exit(1)

print(f"✅ Found API key: {api_key[:10]}...")

# Test document
test_document = """
FINANCIAL DATA TEST
Revenue: $100,000,000
Net Income: $20,000,000
Total Assets: $150,000,000
"""

# Test endpoint
base_url = "https://api.va.landing.ai/v1/ade/parse"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print(f"\n🔍 Testing LandingAI API endpoint: {base_url}\n")

# Test 1: Plain text as 'document'
print("Test 1: Plain text as 'document'")
payload1 = {
    "prompt": "Extract revenue from this document",
    "document": test_document,
    "response_format": "json"
}

response1 = requests.post(base_url, json=payload1, headers=headers)
print(f"  Status: {response1.status_code}")
print(f"  Response: {response1.text[:200]}\n")

# Test 2: Base64 encoded
print("Test 2: Base64 encoded document")
doc_b64 = base64.b64encode(test_document.encode('utf-8')).decode('utf-8')
payload2 = {
    "prompt": "Extract revenue from this document",
    "document": doc_b64,
    "document_type": "text",
    "response_format": "json"
}

response2 = requests.post(base_url, json=payload2, headers=headers)
print(f"  Status: {response2.status_code}")
print(f"  Response: {response2.text[:200]}\n")

# Test 3: With model specified
print("Test 3: With model specified")
payload3 = {
    "prompt": "Extract revenue from this document",
    "document": test_document,
    "model": "dpt-2-latest",
    "response_format": "json"
}

response3 = requests.post(base_url, json=payload3, headers=headers)
print(f"  Status: {response3.status_code}")
print(f"  Response: {response3.text[:200]}\n")

# Test 4: Minimal payload
print("Test 4: Minimal payload")
payload4 = {
    "prompt": "Extract revenue",
    "document": test_document
}

response4 = requests.post(base_url, json=payload4, headers=headers)
print(f"  Status: {response4.status_code}")
print(f"  Response: {response4.text[:200]}\n")

# Test 5: document_url instead
print("Test 5: Using document_url (will fail, just testing format)")
payload5 = {
    "prompt": "Extract revenue",
    "document_url": "https://example.com/test.pdf"
}

response5 = requests.post(base_url, json=payload5, headers=headers)
print(f"  Status: {response5.status_code}")
print(f"  Response: {response5.text[:200]}\n")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

tests = [
    ("Plain 'document'", response1),
    ("Base64 'document'", response2),
    ("With model", response3),
    ("Minimal", response4),
    ("document_url", response5)
]

for name, resp in tests:
    status = "✅ SUCCESS" if resp.status_code == 200 else f"❌ {resp.status_code}"
    print(f"{name:20s}: {status}")

print("\n💡 Check which test succeeded above and we'll use that format!")
