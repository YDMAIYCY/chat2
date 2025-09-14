#!/usr/bin/env python3
"""
Test local functionality of the web scraper without network requests
测试网页抓取器的本地功能（无需网络请求）
"""

from web_scraper import WebScraper, extract_scraping_commands, extract_urls_from_text
from bs4 import BeautifulSoup
import tempfile
import os

def test_command_extraction():
    """Test Chinese command extraction"""
    print("测试中文命令提取")
    print("=" * 40)
    
    test_cases = [
        {
            "text": "抓取网页: https://example.com",
            "expected_count": 1,
            "expected_command": "抓取网页: https://example.com"
        },
        {
            "text": "爬取网页 https://test.com 获取网页信息: https://demo.com",
            "expected_count": 2,
            "expected_urls": ["https://test.com", "https://demo.com"]
        },
        {
            "text": "请帮我scrape https://api.com的内容",
            "expected_count": 1,
            "expected_command": "scrape https://api.com"
        },
        {
            "text": "这是一个链接 https://auto-detect.com 请查看",
            "expected_count": 1,
            "expected_command": "auto_detect"
        },
        {
            "text": "没有任何网址的文本",
            "expected_count": 0
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"输入: {test_case['text']}")
        
        commands = extract_scraping_commands(test_case['text'])
        print(f"提取到 {len(commands)} 个命令")
        
        if len(commands) == test_case['expected_count']:
            print("✅ 命令数量正确")
        else:
            print(f"❌ 期望 {test_case['expected_count']} 个命令，实际 {len(commands)} 个")
        
        for cmd in commands:
            print(f"  - 命令类型: {cmd['command']}")
            print(f"    网址: {cmd['url']}")

def test_url_extraction():
    """Test URL extraction from text"""
    print("\n\n测试网址提取")
    print("=" * 40)
    
    test_texts = [
        "访问 https://www.example.com 了解更多",
        "看看这个网站 http://test.org/path?param=value",
        "www.example.com 这也是一个网址",
        "https://sub.domain.com/path#anchor 很有趣",
        "没有网址的纯文本",
        "多个网址: https://first.com http://second.org www.third.net"
    ]
    
    for text in test_texts:
        urls = extract_urls_from_text(text)
        print(f"\n输入: {text}")
        print(f"提取到的网址: {urls}")

def test_url_validation():
    """Test URL validation and sanitization"""
    print("\n\n测试网址验证和清理")
    print("=" * 40)
    
    scraper = WebScraper()
    
    test_urls = [
        ("https://example.com", True, "完整HTTPS网址"),
        ("http://example.com", True, "完整HTTP网址"),
        ("example.com", True, "自动添加协议"),
        ("www.example.com", True, "www子域名"),
        ("", False, "空网址"),
        ("not-a-url", True, "无效格式（会被自动修正）"),
        ("ftp://example.com", False, "非HTTP协议"),
        ("javascript:alert('xss')", False, "恶意脚本"),
    ]
    
    for url, should_succeed, description in test_urls:
        print(f"\n测试: {description}")
        print(f"输入: '{url}'")
        
        try:
            validated_url = scraper.validate_url(url)
            print(f"✅ 验证成功: {validated_url}")
            if not should_succeed:
                print("⚠️  期望失败但实际成功")
        except ValueError as e:
            print(f"❌ 验证失败: {str(e)}")
            if should_succeed:
                print("⚠️  期望成功但实际失败")

def test_html_parsing():
    """Test HTML content parsing with local HTML"""
    print("\n\n测试HTML内容解析")
    print("=" * 40)
    
    # Create a sample HTML file
    sample_html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>测试页面标题</title>
        <meta name="description" content="这是一个测试页面的描述信息">
        <meta property="og:title" content="Open Graph 标题">
        <meta property="og:description" content="Open Graph 描述">
        <meta property="og:image" content="https://example.com/image.jpg">
    </head>
    <body>
        <h1>主标题</h1>
        <p>这是第一段内容，包含了一些有用的信息。</p>
        <p>这是第二段内容，用来测试文本提取功能。</p>
        
        <div>
            <a href="https://example.com/link1">链接1</a>
            <a href="/relative-link">相对链接</a>
            <a href="#anchor">锚点链接</a>
        </div>
        
        <img src="https://example.com/image1.jpg" alt="图片1">
        <img src="/relative-image.png" alt="图片2">
        
        <script>console.log("这段脚本应该被忽略");</script>
        <style>body { color: red; }</style>
    </body>
    </html>
    '''
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(sample_html, 'lxml')
    scraper = WebScraper()
    
    # Test individual extraction methods
    print("提取测试:")
    
    title = scraper._extract_title(soup)
    print(f"标题: {title}")
    
    description = scraper._extract_description(soup)
    print(f"描述: {description}")
    
    content = scraper._extract_text_content(soup)
    print(f"文本内容 ({len(content)} 字符): {content[:100]}...")
    
    links = scraper._extract_links(soup, "https://example.com")
    print(f"链接数量: {len(links)}")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link['text']} -> {link['url']}")
    
    images = scraper._extract_images(soup, "https://example.com")
    print(f"图片数量: {len(images)}")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img['alt']} -> {img['url']}")
    
    meta_info = scraper._extract_meta_info(soup)
    print(f"Meta信息: {len(meta_info)} 项")
    for key, value in meta_info.items():
        print(f"  {key}: {value}")
    
    og_info = scraper._extract_open_graph(soup)
    print(f"Open Graph信息: {len(og_info)} 项")
    for key, value in og_info.items():
        print(f"  {key}: {value}")

def test_error_handling():
    """Test error handling for various scenarios"""
    print("\n\n测试错误处理")
    print("=" * 40)
    
    scraper = WebScraper(timeout=1)  # Very short timeout
    
    # Test error result structure
    error_result = scraper._error_result("https://example.com", "测试错误")
    
    expected_keys = ['url', 'status_code', 'title', 'description', 'content', 
                     'links', 'images', 'meta_info', 'og_info', 'success', 'error']
    
    print("错误结果结构测试:")
    for key in expected_keys:
        if key in error_result:
            print(f"✅ {key}: {error_result[key]}")
        else:
            print(f"❌ 缺少键: {key}")
    
    # Test that success is False and error is set
    if not error_result['success'] and error_result['error'] == "测试错误":
        print("✅ 错误结果格式正确")
    else:
        print("❌ 错误结果格式不正确")

if __name__ == "__main__":
    print("网页抓取器本地功能测试")
    print("=" * 60)
    
    try:
        test_command_extraction()
        test_url_extraction()
        test_url_validation()
        test_html_parsing()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ 所有本地功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()