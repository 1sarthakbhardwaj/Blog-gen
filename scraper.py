"""
Web scraper for extracting article content from URLs
Uses BeautifulSoup4 + Selenium for better content extraction
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import time


def scrape_article_selenium(url: str, timeout: int = 30) -> Dict[str, str]:
    """
    Scrape article content using Selenium (handles JavaScript)
    
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
        # Validate URL format
        if not url or not url.strip():
            result['error'] = "Empty URL provided"
            return result
        
        url = url.strip()
        
        # Check if URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            result['error'] = f"Invalid URL: Must start with http:// or https://. Got: '{url[:50]}...'"
            return result
        
        # Basic URL validation
        if not re.match(r'https?://[^\s]+', url):
            result['error'] = f"Invalid URL format: '{url[:50]}...'"
            return result
        
        # Try to import selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            result['error'] = "Selenium not installed. Run: pip install selenium"
            return result
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = None
        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(timeout)
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract title
            try:
                title_element = driver.find_element(By.TAG_NAME, "h1")
                result['title'] = title_element.text.strip()
            except:
                result['title'] = driver.title
            
            # Extract content from multiple possible containers
            content_selectors = [
                "article",
                "main",
                "[role='main']",
                ".content",
                ".article",
                ".post",
                ".entry",
                "#content",
                "#article",
                "#post",
                "#entry"
            ]
            
            content_text = ""
            for selector in content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        content_text = elements[0].text
                        if len(content_text) > 100:  # If we found substantial content
                            break
                except:
                    continue
            
            # If no specific container found, get all text
            if not content_text or len(content_text) < 100:
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    content_text = body.text
                except:
                    content_text = driver.page_source
            
            # Clean up the content
            if content_text:
                # Remove extra whitespace
                content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
                content_text = re.sub(r' +', ' ', content_text)
                content_text = content_text.strip()
                
                result['content'] = content_text
            else:
                result['error'] = "Could not extract content from the page"
                
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        result['error'] = f"Selenium scraping error: {str(e)}"
    
    return result


def scrape_article(url: str, timeout: int = 30) -> Dict[str, str]:
    """
    Scrape article content from a given URL
    Uses Selenium for better JavaScript support and content extraction
    
    Args:
        url: The URL of the article to scrape
        timeout: Request timeout in seconds (increased to 30)
    
    Returns:
        Dictionary with 'title', 'content', and 'error' keys
    """
    # Try Selenium first (better for JavaScript sites)
    result = scrape_article_selenium(url, timeout)
    
    # If Selenium fails, fall back to requests + BeautifulSoup
    if result['error'] and "Selenium not installed" not in result['error']:
        return _scrape_with_requests(url, timeout)
    
    return result


def _scrape_with_requests(url: str, timeout: int = 30) -> Dict[str, str]:
    """
    Fallback scraper using requests + BeautifulSoup
    """
    result = {
        'title': '',
        'content': '',
        'error': None
    }
    
    try:
        # Validate URL format
        if not url or not url.strip():
            result['error'] = "Empty URL provided"
            return result
        
        url = url.strip()
        
        # Check if URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            result['error'] = f"Invalid URL: Must start with http:// or https://. Got: '{url[:50]}...'"
            return result
        
        # Basic URL validation
        if not re.match(r'https?://[^\s]+', url):
            result['error'] = f"Invalid URL format: '{url[:50]}...'"
            return result
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
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
            # Extract from all text elements (not just paragraphs)
            text_elements = content.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            text_content = '\n\n'.join([elem.get_text().strip() for elem in text_elements if elem.get_text().strip()])
            
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

