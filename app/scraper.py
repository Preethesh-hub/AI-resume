import requests
from bs4 import BeautifulSoup

def scrape_job_description(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, header, footer, nav elements
        for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            element.decompose()
            
        text = soup.get_text(separator='\n')
        
        # Clean up empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        clean_text = '\n'.join(lines)
        return clean_text
    except Exception as e:
        raise Exception(f"Failed to scrape URL: {str(e)}")
