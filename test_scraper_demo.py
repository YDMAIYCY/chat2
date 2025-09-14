#!/usr/bin/env python3
"""
Test script for the web scraper functionality
测试网页抓取功能的脚本
"""

from web_scraper import WebScraper, extract_scraping_commands, scrape_from_text
import json

def test_command_extraction():
    """Test extraction of scraping commands from Chinese text"""
    print("=" * 50)
    print("测试中文命令提取")
    print("=" * 50)
    
    test_texts = [
        "抓取网页: https://httpbin.org/html",
        "爬取网页 https://httpbin.org/json",
        "获取网页信息: https://httpbin.org/user-agent",
        "请帮我 scrape https://httpbin.org/headers",
        "直接发送网址 https://httpbin.org/ip",
        "这个网站很有趣 https://httpbin.org/uuid 你看看",
    ]
    
    for text in test_texts:
        commands = extract_scraping_commands(text)
        print(f"输入: {text}")
        print(f"提取的命令: {commands}")
        print()

def test_scraper_basic():
    """Test basic scraper functionality"""
    print("=" * 50)
    print("测试基本抓取功能")
    print("=" * 50)
    
    scraper = WebScraper(timeout=10)
    
    # Test with a simple HTML page
    test_url = "https://httpbin.org/html"
    print(f"抓取测试网页: {test_url}")
    
    try:
        result = scraper.extract_content(test_url)
        print(f"抓取成功: {result['success']}")
        if result['success']:
            print(f"标题: {result['title']}")
            print(f"描述: {result['description']}")
            print(f"内容长度: {len(result['content'])} 字符")
            print(f"链接数量: {len(result['links'])}")
            print(f"图片数量: {len(result['images'])}")
        else:
            print(f"错误信息: {result['error']}")
        print()
    except Exception as e:
        print(f"测试异常: {str(e)}")

def test_invalid_url():
    """Test handling of invalid URLs"""
    print("=" * 50)
    print("测试无效网址处理")
    print("=" * 50)
    
    scraper = WebScraper()
    
    invalid_urls = [
        "not-a-url",
        "ftp://example.com",
        "javascript:alert('xss')",
        "",
        "https://this-domain-should-not-exist-12345.com"
    ]
    
    for url in invalid_urls:
        print(f"测试无效网址: {url}")
        result = scraper.extract_content(url)
        print(f"抓取成功: {result['success']}")
        if not result['success']:
            print(f"错误信息: {result['error']}")
        print()

def test_text_scraping():
    """Test scraping from text containing multiple commands"""
    print("=" * 50)
    print("测试文本中的多个抓取命令")
    print("=" * 50)
    
    test_text = """
    你好，请帮我抓取这些网页：
    抓取网页: https://httpbin.org/json
    还有这个：爬取网页 https://httpbin.org/uuid
    以及直接的网址：https://httpbin.org/ip
    """
    
    print(f"输入文本:\n{test_text}")
    
    results = scrape_from_text(test_text, timeout=10)
    print(f"\n找到 {len(results)} 个抓取命令")
    
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  命令: {result.get('command', 'N/A')}")
        print(f"  网址: {result['url']}")
        print(f"  成功: {result['success']}")
        if result['success']:
            print(f"  标题: {result['title']}")
        else:
            print(f"  错误: {result['error']}")

if __name__ == "__main__":
    print("网页抓取功能测试脚本")
    print("Web Scraper Test Script")
    print("=" * 80)
    
    try:
        test_command_extraction()
        test_scraper_basic()
        test_invalid_url()
        test_text_scraping()
        
        print("=" * 50)
        print("所有测试完成！")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试异常: {str(e)}")
        import traceback
        traceback.print_exc()