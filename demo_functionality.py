#!/usr/bin/env python3
"""
Complete demonstration of the web scraping functionality
网页抓取功能完整演示
"""

from web_scraper import WebScraper, extract_scraping_commands, scrape_from_text
import json

def print_banner(title):
    """Print a formatted banner"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def demo_command_extraction():
    """Demonstrate Chinese command extraction"""
    print_banner("中文命令提取演示 / Chinese Command Extraction Demo")
    
    demo_messages = [
        "抓取网页: https://www.python.org",
        "请帮我爬取网页 https://github.com/microsoft/vscode",
        "获取网页信息: https://stackoverflow.com/questions/tagged/python",
        "我想看看这个网站 https://docs.python.org/3/tutorial/",
        "这个链接很有用 https://realpython.com 你可以看看",
        "你能scrape https://news.ycombinator.com 的内容吗？",
    ]
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n示例 {i}:")
        print(f"用户输入: {message}")
        
        commands = extract_scraping_commands(message)
        print(f"检测到 {len(commands)} 个抓取命令:")
        
        for j, cmd in enumerate(commands, 1):
            print(f"  {j}. 命令类型: {cmd['command']}")
            print(f"     目标网址: {cmd['url']}")

def demo_url_validation():
    """Demonstrate URL validation"""
    print_banner("网址验证演示 / URL Validation Demo")
    
    test_urls = [
        "python.org",
        "https://github.com",
        "http://example.com/path?param=value#anchor",
        "www.stackoverflow.com",
        "javascript:alert('xss')",
        "ftp://files.example.com",
        "",
        "not-a-valid-url",
    ]
    
    scraper = WebScraper()
    
    for url in test_urls:
        print(f"\n测试网址: '{url}'")
        try:
            validated = scraper.validate_url(url)
            print(f"✅ 验证通过: {validated}")
        except ValueError as e:
            print(f"❌ 验证失败: {e}")

def demo_api_response_format():
    """Demonstrate API response format"""
    print_banner("API响应格式演示 / API Response Format Demo")
    
    scraper = WebScraper()
    
    # Create a mock successful response
    print("成功响应示例 (Success Response Example):")
    success_response = {
        "url": "https://example.com",
        "status_code": 200,
        "title": "Example Domain",
        "description": "This domain is for use in illustrative examples",
        "content": "Example Domain This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.",
        "links": [
            {"url": "https://www.iana.org/domains/example", "text": "More information..."}
        ],
        "images": [],
        "meta_info": {
            "description": "This domain is for use in illustrative examples"
        },
        "og_info": {},
        "success": True,
        "error": None
    }
    
    print(json.dumps(success_response, indent=2, ensure_ascii=False))
    
    print("\n" + "-" * 40)
    print("错误响应示例 (Error Response Example):")
    
    error_response = scraper._error_result("https://invalid-domain.com", "连接失败: 域名不存在")
    print(json.dumps(error_response, indent=2, ensure_ascii=False))

def demo_chat_integration():
    """Demonstrate chat integration format"""
    print_banner("聊天集成演示 / Chat Integration Demo")
    
    print("用户在聊天中发送的消息示例:")
    print("User message examples in chat:")
    
    chat_messages = [
        "抓取网页: https://www.python.org",
        "帮我获取网页信息 https://github.com/python/cpython",
        "这个网站很有趣 https://docs.python.org 你看看",
    ]
    
    for msg in chat_messages:
        print(f"\n📱 用户消息: {msg}")
        
        commands = extract_scraping_commands(msg)
        if commands:
            print(f"🤖 系统检测: 发现 {len(commands)} 个抓取请求")
            
            # Simulate the formatted response that would be sent to chat
            print("🤖 AI回复格式预览:")
            print("```")
            print("🌐 **网页抓取结果**")
            print("")
            print(f"**网址**: {commands[0]['url']}")
            print("**标题**: [由于网络限制，无法显示实际内容]")
            print("**描述**: [在实际使用中会显示网页描述]")
            print("")
            print("**内容摘要**:")
            print("[在实际使用中会显示网页的文本内容摘要]")
            print("")
            print("**链接数量**: [会显示发现的链接数量]")
            print("**图片数量**: [会显示发现的图片数量]")
            print("```")
        else:
            print("🤖 系统检测: 无抓取命令，将正常处理为聊天消息")

def demo_security_features():
    """Demonstrate security features"""
    print_banner("安全功能演示 / Security Features Demo")
    
    print("安全检查包括 / Security checks include:")
    print("1. 协议验证 - 只允许 HTTP/HTTPS")
    print("2. 恶意URL检测 - 阻止 JavaScript/Data URLs")
    print("3. 网址格式验证 - 确保URL格式正确")
    print("4. 内容长度限制 - 防止资源滥用")
    print("5. 超时设置 - 防止请求卡死")
    
    malicious_urls = [
        "javascript:alert('XSS')",
        "data:text/html,<script>alert('XSS')</script>",
        "file:///etc/passwd",
        "ftp://malicious-site.com",
    ]
    
    scraper = WebScraper()
    
    print("\n恶意URL测试结果:")
    for url in malicious_urls:
        try:
            scraper.validate_url(url)
            print(f"⚠️  {url} - 未被阻止（需要改进）")
        except ValueError as e:
            print(f"✅ {url} - 已阻止: {e}")

if __name__ == "__main__":
    print("🌐 网页抓取功能完整演示")
    print("🌐 Web Scraping Functionality Complete Demo")
    print("=" * 60)
    print("作者: Copilot Coding Agent")
    print("项目: YDMAIYCY/chat2")
    print("功能: Python网页抓取集成到聊天应用")
    
    try:
        demo_command_extraction()
        demo_url_validation()
        demo_api_response_format()
        demo_chat_integration()
        demo_security_features()
        
        print_banner("演示完成 / Demo Complete")
        print("✅ 所有功能演示完成！")
        print("✅ All functionality demonstrations completed!")
        print("\n🚀 部署说明 / Deployment Instructions:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 启动服务: python3 app.py")
        print("3. 访问应用: http://localhost:5000")
        print("4. API接口: POST http://localhost:5000/api/scrape")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()