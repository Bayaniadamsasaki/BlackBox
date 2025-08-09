# plugins/crawl_simple.py
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from .base import Plugin
from rich.console import Console

console = Console()

class SimpleCrawler(Plugin):
    name = "Simple Crawler (Python)"
    category = "Crawler"
    description = "Basic Python-based web crawler"
    bin_name = "python"  # Always available since we're running in Python

    def __init__(self):
        super().__init__()
        try:
            import requests
            import bs4
        except ImportError:
            console.print("[red]Missing dependencies: requests, beautifulsoup4[/red]")
            console.print("Install with: pip install requests beautifulsoup4")
    
    def clean_url_for_filename(self, url: str) -> str:
        """Clean URL for safe filename"""
        cleaned = url.replace('://', '_').replace('/', '_')
        # Remove invalid filename characters  
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', cleaned)
        return cleaned
    
    def is_available(self) -> bool:
        try:
            import requests
            import bs4
            return True
        except ImportError:
            return False

    def run(self, url: str, out_dir="reports", depth=2, headless=False, extra=""):
        self.ensure_reports_dir(out_dir)
        out = f"{out_dir}/simple_crawler_{self.clean_url_for_filename(url)}.txt"
        
        console.print(f"[cyan]Starting simple crawl of {url} (depth: {depth})[/cyan]")
        
        visited = set()
        to_visit = [(url, 0)]  # (url, current_depth)
        found_urls = []
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        while to_visit:
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > depth:
                continue
                
            visited.add(current_url)
            
            try:
                console.print(f"[dim]Crawling: {current_url} (depth: {current_depth})[/dim]")
                response = session.get(current_url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    found_urls.append(current_url)
                    
                    # Parse HTML untuk cari links baru
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Cari semua links
                        for link in soup.find_all('a', href=True):
                            href = link['href'].strip()
                            if href:
                                absolute_url = urljoin(current_url, href)
                                parsed = urlparse(absolute_url)
                                
                                # Hanya crawl dari domain yang sama
                                if parsed.netloc == urlparse(url).netloc:
                                    if absolute_url not in visited and current_depth < depth:
                                        to_visit.append((absolute_url, current_depth + 1))
                                        
                        # Cari form actions
                        for form in soup.find_all('form', action=True):
                            action = form['action'].strip()
                            if action:
                                absolute_url = urljoin(current_url, action)
                                parsed = urlparse(absolute_url)
                                if parsed.netloc == urlparse(url).netloc:
                                    found_urls.append(absolute_url)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                console.print(f"[red]Error crawling {current_url}: {str(e)}[/red]")
                continue
        
        # Save results
        with open(out, 'w', encoding='utf-8') as f:
            for found_url in sorted(set(found_urls)):
                f.write(found_url + '\n')
        
        console.print(f"[green]Found {len(set(found_urls))} unique URLs[/green]")
        return out
