"""
Internet Handler Module
Handles web search and content fetching
Privacy-focused with DuckDuckGo
"""

import requests
from bs4 import BeautifulSoup
from config import config
import time

class InternetHandler:
    """Manages web search and content retrieval"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': config.USER_AGENT
        }
        print("🌐 Internet Handler initialized")
        print(f"   Search engine: {config.SEARCH_ENGINE}")
    
    def search_web(self, query, max_results=None):
        """
        Search the web using DuckDuckGo
        Returns list of results with title, url, snippet
        """
        if max_results is None:
            max_results = config.MAX_SEARCH_RESULTS
        
        try:
            from duckduckgo_search import DDGS
            
            print(f"Searching: {query}")
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", "No title"),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", "No description")
                    })
            
            print(f"✅ Found {len(results)} results")
            return results
            
        except ImportError:
            print("⚠️ duckduckgo-search not installed, trying alternative...")
            return self._search_web_fallback(query, max_results)
        except Exception as e:
            print(f"⚠️ Search error: {e}")
            return []
    
    def _search_web_fallback(self, query, max_results):
        """Fallback search method using direct requests"""
        try:
            # Use DuckDuckGo lite HTML version
            url = f"https://lite.duckduckgo.com/lite/?q={requests.utils.quote(query)}"
            
            response = requests.get(
                url, 
                headers=self.headers,
                timeout=config.SEARCH_TIMEOUT
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_divs = soup.find_all('tr', limit=max_results * 2)
            
            for div in result_divs:
                # Extract title link
                title_link = div.find('a', class_='result-link')
                if title_link:
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Extract snippet
                    snippet_elem = div.find('td', class_='result-snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                
                if len(results) >= max_results:
                    break
            
            print(f"✅ Found {len(results)} results (fallback)")
            return results
            
        except Exception as e:
            print(f"⚠️ Fallback search error: {e}")
            return []
    
    def fetch_url(self, url, max_length=None):
        """
        Fetch content from a URL
        Returns cleaned text content
        """
        if max_length is None:
            max_length = config.MAX_CONTENT_LENGTH
        
        try:
            print(f"Fetching: {url}")
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=config.FETCH_TIMEOUT,
                allow_redirects=True
            )
            
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Truncate if too long
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Content truncated...]"
            
            print(f"✅ Fetched {len(text)} characters")
            return text
            
        except requests.exceptions.Timeout:
            return "⚠️ Request timed out"
        except requests.exceptions.RequestException as e:
            return f"⚠️ Error fetching URL: {e}"
        except Exception as e:
            return f"⚠️ Unexpected error: {e}"
    
    def fetch_url_metadata(self, url):
        """
        Fetch metadata from a URL (title, description, etc.)
        """
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=config.FETCH_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            metadata = {
                "url": url,
                "title": None,
                "description": None,
                "author": None,
                "published_date": None
            }
            
            # Get title
            title_tag = soup.find('title')
            if title_tag:
                metadata["title"] = title_tag.get_text(strip=True)
            
            # Get meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                metadata["description"] = desc_tag.get('content', '')
            
            # Get Open Graph data
            og_title = soup.find('meta', property='og:title')
            if og_title and not metadata["title"]:
                metadata["title"] = og_title.get('content', '')
            
            og_desc = soup.find('meta', property='og:description')
            if og_desc and not metadata["description"]:
                metadata["description"] = og_desc.get('content', '')
            
            # Get author
            author_tag = soup.find('meta', attrs={'name': 'author'})
            if author_tag:
                metadata["author"] = author_tag.get('content', '')
            
            return metadata
            
        except Exception as e:
            print(f"⚠️ Error fetching metadata: {e}")
            return {"url": url, "error": str(e)}
    
    def search_and_fetch(self, query, fetch_first=True):
        """
        Search and optionally fetch content from first result
        Returns search results and optionally the content
        """
        results = self.search_web(query)
        
        if not results:
            return {
                "query": query,
                "results": [],
                "content": None
            }
        
        data = {
            "query": query,
            "results": results,
            "content": None
        }
        
        if fetch_first and results:
            first_url = results[0]["url"]
            print(f"Fetching first result: {first_url}")
            data["content"] = self.fetch_url(first_url)
        
        return data
    
    def download_file(self, url, filename=None):
        """
        Download a file from URL
        Returns filepath or None
        """
        try:
            from pathlib import Path
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=config.FETCH_TIMEOUT,
                stream=True
            )
            response.raise_for_status()
            
            # Determine filename
            if not filename:
                from urllib.parse import urlparse
                filename = Path(urlparse(url).path).name
                if not filename:
                    filename = "download.bin"
            
            # Save to downloads directory
            filepath = Path(config.DOWNLOADS_DIR) / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"✅ Downloaded: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"⚠️ Download error: {e}")
            return None
    
    def check_url_status(self, url):
        """Check if URL is accessible"""
        try:
            response = requests.head(
                url,
                headers=self.headers,
                timeout=5,
                allow_redirects=True
            )
            
            return {
                "url": url,
                "status_code": response.status_code,
                "accessible": response.status_code < 400,
                "content_type": response.headers.get('content-type', 'unknown')
            }
            
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "accessible": False,
                "error": str(e)
            }

# Global internet handler instance
internet_handler = InternetHandler()
