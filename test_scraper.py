#!/usr/bin/env python3
"""
Simple test script for web scraping functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from web_scraper import WebScraper, format_scrape_result

def test_basic_scraping():
    """测试基本的网页抓取功能"""
    print("🧪 测试基本网页抓取功能...")
    
    scraper = WebScraper()
    
    # 测试有效URL
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com",
    ]
    
    for url in test_urls:
        print(f"\n📝 测试URL: {url}")
        result = scraper.scrape_webpage(url)
        
        if result['success']:
            print(f"✅ 成功抓取")
            print(f"   标题: {result['title']}")
            print(f"   描述: {result['description'][:100]}...")
            print(f"   链接数: {len(result['links'])}")
            print(f"   图片数: {len(result['images'])}")
        else:
            print(f"❌ 抓取失败: {result['error']}")
    
    # 测试无效URL
    print(f"\n📝 测试无效URL:")
    invalid_result = scraper.scrape_webpage("invalid-url")
    if not invalid_result['success']:
        print(f"✅ 正确识别无效URL: {invalid_result['error']}")
    else:
        print(f"❌ 应该识别为无效URL")

def test_url_validation():
    """测试URL验证功能"""
    print("\n🧪 测试URL验证功能...")
    
    scraper = WebScraper()
    
    valid_urls = [
        "https://example.com",
        "http://test.com/page",
        "https://sub.domain.com/path?param=value"
    ]
    
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",
        "",
        "javascript:alert('xss')"
    ]
    
    print("✅ 有效URL测试:")
    for url in valid_urls:
        is_valid = scraper.validate_url(url)
        print(f"   {url}: {'✅' if is_valid else '❌'}")
    
    print("\n❌ 无效URL测试:")
    for url in invalid_urls:
        is_valid = scraper.validate_url(url)
        print(f"   {url}: {'❌ (正确)' if not is_valid else '✅ (错误)'}")

def test_format_result():
    """测试结果格式化功能"""
    print("\n🧪 测试结果格式化...")
    
    # 模拟成功结果
    success_result = {
        'success': True,
        'url': 'https://example.com',
        'title': '测试标题',
        'description': '这是一个测试描述',
        'text_content': '这是网页的文本内容，用于测试格式化功能。' * 20,
        'links': [
            {'url': 'https://example.com/page1', 'text': '页面1', 'title': ''},
            {'url': 'https://example.com/page2', 'text': '页面2', 'title': ''},
        ],
        'images': [
            {'url': 'https://example.com/img1.jpg', 'alt': '图片1', 'title': ''},
        ],
        'status_code': 200,
        'content_type': 'text/html',
        'content_length': 1234
    }
    
    formatted = format_scrape_result(success_result)
    print("✅ 成功结果格式化:")
    print(formatted[:300] + "...")
    
    # 模拟失败结果
    error_result = {
        'success': False,
        'error': '网络连接超时',
        'url': 'https://timeout-example.com'
    }
    
    formatted_error = format_scrape_result(error_result)
    print("\n❌ 错误结果格式化:")
    print(formatted_error)

if __name__ == "__main__":
    print("🚀 开始网页爬虫测试...")
    
    try:
        test_url_validation()
        test_format_result() 
        test_basic_scraping()
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        sys.exit(1)