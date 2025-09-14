"""
Web scraping module for extracting webpage information
支持从网页抓取标题、文本内容、链接等信息
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, timeout: int = 10):
        """
        初始化网页爬虫
        
        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        # 设置用户代理，避免被反爬虫机制阻止
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def validate_url(self, url: str) -> bool:
        """
        验证URL是否有效
        
        Args:
            url: 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def scrape_webpage(self, url: str) -> Dict:
        """
        抓取网页信息
        
        Args:
            url: 要抓取的网页URL
            
        Returns:
            Dict: 包含网页信息的字典
        """
        if not self.validate_url(url):
            return {
                'success': False,
                'error': 'Invalid URL format',
                'url': url
            }
        
        try:
            logger.info(f"开始抓取网页: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取基本信息
            result = {
                'success': True,
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'text_content': self._extract_text_content(soup),
                'links': self._extract_links(soup, url),
                'images': self._extract_images(soup, url),
                'meta_info': self._extract_meta_info(soup),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.text)
            }
            
            logger.info(f"成功抓取网页: {url}, 标题: {result['title']}")
            return result
            
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout for URL: {url}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'url': url
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for URL {url}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'url': url
            }
        except Exception as e:
            error_msg = f"Unexpected error scraping {url}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'url': url
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取网页标题"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # 如果没有title标签，尝试从h1标签获取
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "无标题"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取网页描述"""
        # 尝试从meta description获取
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # 尝试从meta property获取（用于Open Graph）
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # 如果没有meta描述，取前200个字符的文本内容
        text_content = self._extract_text_content(soup)
        if text_content:
            return text_content[:200] + "..." if len(text_content) > 200 else text_content
        
        return "无描述"
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """提取网页纯文本内容"""
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取纯文本
        text = soup.get_text()
        
        # 清理文本：移除多余的空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """提取网页中的链接"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # 转换相对链接为绝对链接
            absolute_url = urljoin(base_url, href)
            
            if self.validate_url(absolute_url):
                links.append({
                    'url': absolute_url,
                    'text': text,
                    'title': link.get('title', '')
                })
        
        # 限制返回的链接数量，避免数据过大
        return links[:50]
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """提取网页中的图片"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            alt = img.get('alt', '')
            
            # 转换相对链接为绝对链接
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'url': absolute_url,
                'alt': alt,
                'title': img.get('title', '')
            })
        
        # 限制返回的图片数量
        return images[:20]
    
    def _extract_meta_info(self, soup: BeautifulSoup) -> Dict:
        """提取meta信息"""
        meta_info = {}
        
        # 提取常见的meta标签
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name'):
                meta_info[tag['name']] = tag.get('content', '')
            elif tag.get('property'):
                meta_info[tag['property']] = tag.get('content', '')
        
        return meta_info

def format_scrape_result(result: Dict) -> str:
    """
    格式化抓取结果为可读的文本
    
    Args:
        result: 抓取结果字典
        
    Returns:
        str: 格式化后的文本
    """
    if not result['success']:
        return f"❌ 抓取失败: {result.get('error', '未知错误')}\n🔗 URL: {result.get('url', '')}"
    
    formatted_text = f"""🌐 网页抓取结果

🔗 **URL**: {result['url']}
📄 **标题**: {result['title']}
📝 **描述**: {result['description']}

📊 **基本信息**:
- 状态码: {result['status_code']}
- 内容类型: {result['content_type']}
- 内容长度: {result['content_length']} 字符

🔗 **链接数量**: {len(result['links'])} 个
🖼️ **图片数量**: {len(result['images'])} 个

📋 **文本内容预览** (前500字符):
{result['text_content'][:500]}{"..." if len(result['text_content']) > 500 else ""}
"""

    # 添加主要链接信息
    if result['links']:
        formatted_text += "\n\n🔗 **主要链接**:\n"
        for i, link in enumerate(result['links'][:5], 1):
            formatted_text += f"{i}. [{link['text'][:50]}]({link['url']})\n"
    
    return formatted_text

# 创建全局爬虫实例
scraper = WebScraper()