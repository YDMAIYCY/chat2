"""
Web Scraper Module for Chat2 Application
提供网页抓取功能的模块

Features:
- URL validation and sanitization
- Content extraction (title, description, text, links, images)
- Meta information parsing including Open Graph tags
- Robust error handling for network issues and parsing errors
- Configurable timeout and user-agent settings
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper class with configurable settings and comprehensive extraction capabilities"""
    
    def __init__(self, timeout: int = 10, user_agent: str = None):
        """
        Initialize the web scraper
        
        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def validate_url(self, url: str) -> str:
        """
        Validate and sanitize URL
        
        Args:
            url: URL to validate
            
        Returns:
            Cleaned URL
            
        Raises:
            ValueError: If URL is invalid or uses non-HTTP protocol
        """
        if not url:
            raise ValueError("URL不能为空")
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse and validate URL
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError("无效的URL格式")
        
        if not parsed.netloc:
            raise ValueError("无效的URL格式")
        
        # Security check - only allow HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("只支持HTTP和HTTPS协议")
        
        # Additional security checks
        if any(proto in url.lower() for proto in ['javascript:', 'data:', 'file:', 'ftp:']):
            raise ValueError("不安全的URL协议")
        
        return url
    
    def extract_content(self, url: str) -> Dict[str, Union[str, List[str]]]:
        """
        Extract comprehensive content from a webpage
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing extracted content
        """
        try:
            # Validate URL
            url = self.validate_url(url)
            logger.info(f"开始抓取网页: {url}")
            
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract basic information
            result = {
                'url': url,
                'status_code': response.status_code,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'content': self._extract_text_content(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url),
                'meta_info': self._extract_meta_info(soup),
                'og_info': self._extract_open_graph(soup),
                'success': True,
                'error': None
            }
            
            logger.info(f"成功抓取网页: {url}")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"请求超时: {url}"
            logger.error(error_msg)
            return self._error_result(url, error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = f"连接失败: {url}"
            logger.error(error_msg)
            return self._error_result(url, error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误 {e.response.status_code}: {url}"
            logger.error(error_msg)
            return self._error_result(url, error_msg)
            
        except ValueError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return self._error_result(url, error_msg)
            
        except Exception as e:
            error_msg = f"抓取失败: {str(e)}"
            logger.error(error_msg)
            return self._error_result(url, error_msg)
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "无标题"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description from meta tags"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Fallback to first paragraph
        p_tag = soup.find('p')
        if p_tag:
            text = p_tag.get_text().strip()
            if len(text) > 50:
                return text[:200] + ('...' if len(text) > 200 else '')
        
        return "无描述"
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000] + '...'
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text().strip()
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            if full_url and text:
                links.append({
                    'url': full_url,
                    'text': text
                })
        
        return links[:20]  # Limit to first 20 links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from the page"""
        images = []
        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            alt = img_tag.get('alt', '')
            
            if src:
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, src)
                images.append({
                    'url': full_url,
                    'alt': alt
                })
        
        return images[:10]  # Limit to first 10 images
    
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta information"""
        meta_info = {}
        
        # Extract common meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            
            if name and content:
                meta_info[name] = content
        
        return meta_info
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract Open Graph meta information"""
        og_info = {}
        
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        for tag in og_tags:
            property_name = tag.get('property')
            content = tag.get('content')
            
            if property_name and content:
                # Remove 'og:' prefix
                key = property_name.replace('og:', '')
                og_info[key] = content
        
        return og_info
    
    def _error_result(self, url: str, error_msg: str) -> Dict[str, Union[str, bool, None]]:
        """Return error result structure"""
        return {
            'url': url,
            'status_code': None,
            'title': None,
            'description': None,
            'content': None,
            'links': [],
            'images': [],
            'meta_info': {},
            'og_info': {},
            'success': False,
            'error': error_msg
        }


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text
    
    Args:
        text: Text to search for URLs
        
    Returns:
        List of found URLs
    """
    # URL pattern
    url_pattern = re.compile(
        r'(?:(?:https?://)|(?:www\.))(?:[-\w.])+(?:\.[a-zA-Z]{2,3})(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?',
        re.IGNORECASE
    )
    
    urls = url_pattern.findall(text)
    return [url for url in urls if url]


def extract_scraping_commands(text: str) -> List[Dict[str, str]]:
    """
    Extract scraping commands from Chinese text
    
    Args:
        text: Text to search for scraping commands
        
    Returns:
        List of command dictionaries with 'command' and 'url' keys
    """
    commands = []
    
    # Chinese scraping command patterns
    patterns = [
        r'抓取网页[:\s]*([^\s]+)',
        r'爬取网页[:\s]*([^\s]+)',
        r'获取网页信息[:\s]*([^\s]+)',
        r'网页抓取[:\s]*([^\s]+)',
        r'scrape[:\s]*([^\s，。！？]+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.group(1).strip()
            commands.append({
                'command': match.group(0),
                'url': url
            })
    
    # Also check for standalone URLs
    urls = extract_urls_from_text(text)
    for url in urls:
        # Check if URL is not already part of a command
        url_in_command = any(url in cmd['url'] for cmd in commands)
        if not url_in_command:
            commands.append({
                'command': 'auto_detect',
                'url': url
            })
    
    return commands


# Convenience functions for easy use
def scrape_url(url: str, timeout: int = 10) -> Dict[str, Union[str, List[str]]]:
    """
    Convenience function to scrape a single URL
    
    Args:
        url: URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Scraped content dictionary
    """
    scraper = WebScraper(timeout=timeout)
    return scraper.extract_content(url)


def scrape_from_text(text: str, timeout: int = 10) -> List[Dict[str, Union[str, List[str]]]]:
    """
    Convenience function to scrape URLs found in text
    
    Args:
        text: Text containing URLs or scraping commands
        timeout: Request timeout in seconds
        
    Returns:
        List of scraped content dictionaries
    """
    commands = extract_scraping_commands(text)
    scraper = WebScraper(timeout=timeout)
    
    results = []
    for cmd in commands:
        result = scraper.extract_content(cmd['url'])
        result['command'] = cmd['command']
        results.append(result)
    
    return results