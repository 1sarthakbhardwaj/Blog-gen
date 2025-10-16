"""
Web scraper for extracting article content from URLs
Uses BeautifulSoup4 for HTML parsing
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re


def scrape_article(url: str, timeout: int = 10) -> Dict[str, str]:
    """
    Scrape article content from a given URL
    
    Args:
        url: The URL of the article to scrape
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with 'title', 'content', and 'error' keys
    """
    result = {
        'title': '',
        'content': '',
        'error': None
    }
    
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('h1') or soup.find('title')
        if title_tag:
            result['title'] = title_tag.get_text().strip()
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        
        # Try to find main content area
        # Look for common article containers
        content_containers = [
            soup.find('article'),
            soup.find('main'),
            soup.find('div', class_=re.compile(r'(content|article|post|entry)', re.I)),
            soup.find('div', id=re.compile(r'(content|article|post|entry)', re.I))
        ]
        
        content = None
        for container in content_containers:
            if container:
                content = container
                break
        
        # If no specific container found, use body
        if not content:
            content = soup.find('body')
        
        if content:
            # Extract paragraphs
            paragraphs = content.find_all('p')
            text_content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Clean up extra whitespace
            text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
            text_content = re.sub(r' +', ' ', text_content)
            
            result['content'] = text_content
        
        if not result['content']:
            result['error'] = "Could not extract content from the page"
            
    except requests.Timeout:
        result['error'] = f"Request timeout after {timeout} seconds"
    except requests.RequestException as e:
        result['error'] = f"Request failed: {str(e)}"
    except Exception as e:
        result['error'] = f"Scraping error: {str(e)}"
    
    return result


def scrape_multiple_articles(urls: list) -> list:
    """
    Scrape multiple articles from a list of URLs
    
    Args:
        urls: List of article URLs
    
    Returns:
        List of dictionaries with scraped content
    """
    results = []
    for url in urls:
        if url and url.strip():
            result = scrape_article(url.strip())
            results.append(result)
        else:
            results.append({'title': '', 'content': '', 'error': 'Empty URL'})
    
    return results

