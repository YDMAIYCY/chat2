#!/usr/bin/env python3
"""
Demo script showing web scraping functionality
演示网页抓取功能的脚本
"""

from web_scraper import scraper, format_scrape_result

def demo_web_scraping():
    """演示网页抓取功能"""
    print("🌐 网页抓取功能演示")
    print("=" * 50)
    
    # 演示URL验证
    print("\n1. URL验证功能:")
    test_urls = [
        "https://example.com",  # 有效URL
        "invalid-url",          # 无效URL
        "ftp://example.com",    # 非HTTP协议
    ]
    
    for url in test_urls:
        is_valid = scraper.validate_url(url)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"   {url}: {status}")
    
    # 演示命令提取
    print("\n2. 命令提取功能:")
    from app import extract_scrape_command
    
    test_messages = [
        "抓取网页：https://example.com",
        "请帮我分析 https://news.com/article",
        "这是普通聊天消息",
    ]
    
    for message in test_messages:
        extracted_url = extract_scrape_command(message)
        if extracted_url:
            print(f"   '{message}' -> 提取到URL: {extracted_url}")
        else:
            print(f"   '{message}' -> 无URL")
    
    # 演示结果格式化
    print("\n3. 结果格式化功能:")
    sample_result = {
        'success': True,
        'url': 'https://example.com',
        'title': '示例网站',
        'description': '这是一个用于演示的示例网站',
        'text_content': '这里是网页的文本内容，包含了网站的主要信息。',
        'links': [
            {'url': 'https://example.com/page1', 'text': '页面1', 'title': ''},
            {'url': 'https://example.com/page2', 'text': '页面2', 'title': ''},
        ],
        'images': [
            {'url': 'https://example.com/logo.png', 'alt': '网站logo', 'title': ''},
        ],
        'status_code': 200,
        'content_type': 'text/html; charset=utf-8',
        'content_length': 1234
    }
    
    formatted = format_scrape_result(sample_result)
    print(formatted)
    
    print("\n4. 错误处理演示:")
    error_result = {
        'success': False,
        'error': '网络连接超时',
        'url': 'https://timeout-example.com'
    }
    
    formatted_error = format_scrape_result(error_result)
    print(formatted_error)
    
    print("\n✨ 功能特点:")
    print("   • 自动识别和验证URL")
    print("   • 提取网页标题、描述、文本内容")
    print("   • 获取页面中的链接和图片")
    print("   • 支持多种命令格式")
    print("   • 完善的错误处理")
    print("   • 结果格式化展示")
    
    print("\n📝 使用方法:")
    print("   1. 在聊天界面输入：'抓取网页: https://example.com'")
    print("   2. 或直接输入网址，系统会自动识别")
    print("   3. 通过API接口：POST /api/scrape")
    
    print("\n🔧 技术实现:")
    print("   • 使用 requests 库进行HTTP请求")
    print("   • 使用 BeautifulSoup 解析HTML")
    print("   • 集成到 Flask 聊天应用中")
    print("   • 支持 WebSocket 实时通信")

if __name__ == "__main__":
    demo_web_scraping()