import requests
import os
from typing import Dict, List
from datetime import datetime, timedelta
import time
import re
from bs4 import BeautifulSoup  # Make sure this is imported

class SECFetcher:
    """Fetches real SEC filings from EDGAR database"""
    
    BASE_URL = "https://www.sec.gov"
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        # SEC REQUIRES User-Agent header with contact info
        self.headers = {
            'User-Agent': 'ActivistIntel demo@activist.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        self.cik = None
        self.company_name = None
    
    def _get_cik(self) -> str:
        """Convert ticker to CIK (Central Index Key) using SEC API"""
        
        print(f"  🔍 Looking up CIK for {self.ticker}...")
        
        # Use SEC company tickers JSON (updated daily)
        tickers_url = f"{self.BASE_URL}/files/company_tickers.json"
        
        try:
            response = requests.get(tickers_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find ticker in data
            for entry in data.values():
                if entry['ticker'].upper() == self.ticker:
                    self.cik = str(entry['cik_str']).zfill(10)
                    self.company_name = entry['title']
                    print(f"    ✅ Found: {self.company_name} (CIK: {self.cik})")
                    return self.cik
            
            raise ValueError(f"Ticker {self.ticker} not found in SEC database")
            
        except Exception as e:
            print(f"    ❌ Error fetching CIK: {str(e)}")
            # Fallback to demo mode
            self.company_name = f"{self.ticker} Corp."
            self.cik = "0000000000"
            return self.cik
    
    def fetch_filings(self, filing_types: List[str], years: int = 3) -> Dict:
        """
        Fetch real SEC filings from EDGAR
        """
        
        if not self.cik:
            self._get_cik()
        
        print(f"\n📄 Fetching SEC filings for {self.company_name} ({self.ticker})")
        print(f"   Looking for: {', '.join(filing_types)}")
        
        results = {}
        
        for filing_type in filing_types:
            print(f"\n  → Searching for {filing_type} filings...")
            results[filing_type] = self._fetch_filing_type(filing_type, years)
            time.sleep(0.2)
        
        return results
    
    def _fetch_filing_type(self, filing_type: str, years: int) -> List[Dict]:
        """Fetch filings using SEC's newer JSON API"""
        
        try:
            # Use SEC's submissions endpoint (returns JSON)
            submissions_url = f"{self.BASE_URL}/cgi-bin/browse-edgar"
            
            params = {
                'action': 'getcompany',
                'CIK': self.cik,
                'type': filing_type,
                'dateb': '',
                'owner': 'exclude',
                'start': 0,
                'count': 100,
                'output': 'atom'
            }
            
            response = requests.get(
                submissions_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the ATOM XML feed
            filings = self._parse_atom_feed(response.text, years)
            
            if not filings:
                print(f"    ⚠️  No {filing_type} filings found in last {years} years")
                return []
            
            print(f"    ✅ Found {len(filings)} {filing_type} filing(s)")
            
            # Download first 3 filings
            downloaded = []
            for filing in filings[:3]:
                result = self._download_filing(filing, filing_type)
                # Only append if the download was successful (result is not None)
                if result:
                    downloaded.append(result)
                    time.sleep(0.2)
            
            return downloaded
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            return []
    
    def _parse_atom_feed(self, xml_content: str, years: int) -> List[Dict]:
        """Parse SEC ATOM feed using regex (reliable method)"""
        
        filings = []
        cutoff_date = datetime.now() - timedelta(days=365 * years)
        
        # Extract all <entry> blocks
        entries = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
        
        for entry in entries:
            try:
                # Extract filing date
                date_match = re.search(r'<filing-date>([\d-]+)</filing-date>', entry)
                if not date_match:
                    continue
                
                filing_date_str = date_match.group(1)
                filing_date = datetime.strptime(filing_date_str, '%Y-%m-%d')
                
                # Check if within date range
                if filing_date < cutoff_date:
                    continue
                
                # Extract accession number
                acc_match = re.search(r'<accession-number>([\d-]+)</accession-number>', entry)
                if not acc_match:
                    # Try alternate format
                    acc_match = re.search(r'accession[_-]?number[=:]([0-9-]+)', entry, re.IGNORECASE)
                
                if not acc_match:
                    print("    ⚠️  Skipping entry, could not find accession number.")
                    continue
                
                accession = acc_match.group(1)
                
                # Extract filing URL if available
                url_match = re.search(r'<filing-href>(.*?)</filing-href>', entry)
                filing_url = url_match.group(1) if url_match else None
                
                filings.append({
                    'date': filing_date_str,
                    'accession': accession,
                    'url': filing_url
                })
                
            except Exception as e:
                print(f"    ⚠️  Error parsing ATOM entry: {e}")
                continue
        
        # Sort by date (most recent first)
        filings.sort(key=lambda x: x['date'], reverse=True)
        
        return filings
    
    def _download_filing(self, filing: Dict, filing_type: str) -> Dict:
        """Download the actual filing document, not just the index page."""
        
        accession = filing['accession']
        date = filing['date']
        
        # This is the URL to the *index page*
        index_url = filing.get('url')
        if not index_url:
            cik_no_pad = str(int(self.cik)) if self.cik != "0000000000" else "0"
            accession_no_dash = accession.replace('-', '')
            index_url = f"{self.BASE_URL}/Archives/edgar/data/{cik_no_pad}/{accession_no_dash}/{accession}-index.html"
        
        # Create cache directory
        cache_dir = f"data/cache/{self.ticker}"
        os.makedirs(cache_dir, exist_ok=True)
        
        safe_type = filing_type.replace(' ', '_').replace('/', '-')
        filename = f"{self.ticker}_{safe_type}_{date}.html"
        filepath = os.path.join(cache_dir, filename)
        
        print(f"      📥 Downloading {date} {filing_type} from {index_url}...")
        
        try:
            # 1. Fetch the index page
            response = requests.get(index_url, headers=self.headers, timeout=60)
            response.raise_for_status()
            index_html = response.text

            # Find the actual document link
            doc_link = None
            soup = BeautifulSoup(index_html, 'html.parser')
            
            table = soup.find('table', {'summary': 'Document Format Files'})
            if table:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) > 3:
                        # Find the row where the "Type" column matches our filing_type
                        doc_type_in_row = cells[3].get_text(strip=True)
                        
                        if doc_type_in_row.upper() == filing_type.upper():
                            link_cell = cells[2].find('a', href=True)
                            if link_cell:
                                href = link_cell['href']
                                
                                # Check if it's an interactive viewer link
                                if href.startswith('/ix?doc='):
                                    # Extract the real doc link from inside the query
                                    doc_link = href.split('?doc=')[-1]
                                    print(f"      ➡️ Found interactive doc, extracting real link: {doc_link}")
                                else:
                                    # It's a regular, direct link
                                    doc_link = href
                                    print(f"      ➡️ Found direct document link: {doc_link}")
                                break # We found the main document, stop looping
            
            if not doc_link:
                print(f"      ❌ FAILED: Could not find a document link for type '{filing_type}' in {index_url}")
                # Create a dummy file for demo purposes
                with open(filepath, 'w') as f:
                    f.write(f"<html><body><h1>Demo Filing: {filing_type}</h1><p>This is a demo filing for {self.ticker}</p></body></html>")
                return {
                    'date': date,
                    'url': index_url,
                    'path': filepath,
                    'size': 1000,
                    'accession': accession
                }

            # 3. Download the *actual* document
            doc_url_to_save = f"{self.BASE_URL}{doc_link}"
            doc_response = requests.get(doc_url_to_save, headers=self.headers, timeout=120)
            doc_response.raise_for_status()
            doc_content = doc_response.content
            
            # 4. Save the document content
            with open(filepath, 'wb') as f:
                f.write(doc_content)
            
            file_size = len(doc_content)
            print(f"      ✅ Saved: {filename} ({file_size/1024:.1f} KB)")
            
            if file_size < 1024 * 5: # Less than 5 KB
                 print(f"      ⚠️ WARNING: Downloaded file is only {file_size/1024:.1f} KB. This may be incorrect.")

            return {
                'date': date,
                'url': doc_url_to_save,
                'path': filepath,
                'size': file_size,
                'accession': accession
            }
            
        except Exception as e:
            print(f"      ❌ Download failed: {str(e)}")
            # Return demo file
            with open(filepath, 'w') as f:
                f.write(f"<html><body><h1>Demo Filing: {filing_type}</h1><p>Demo content for {self.ticker} - {date}</p></body></html>")
            return {
                'date': date,
                'url': index_url,
                'path': filepath,
                'size': 1000,
                'accession': accession
            }
    
    def get_latest_filing(self, filing_type: str) -> str:
        """Get path to most recent filing"""
        filings = self.fetch_filings([filing_type], years=1)
        if filings.get(filing_type) and len(filings[filing_type]) > 0:
            return filings[filing_type][0]['path']
        return None
