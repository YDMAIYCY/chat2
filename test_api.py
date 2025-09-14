#!/usr/bin/env python3
"""
Test script for web scraping API endpoints
"""

import requests
import json
import time
import subprocess
import sys
import signal
import os

def start_flask_app():
    """启动Flask应用"""
    print("🚀 启动Flask应用...")
    process = subprocess.Popen([sys.executable, 'app.py'], 
                              cwd='/home/runner/work/chat2/chat2',
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # 等待应用启动
    time.sleep(3)
    return process

def test_scrape_api():
    """测试网页抓取API"""
    print("🧪 测试网页抓取API...")
    
    # 测试数据
    test_cases = [
        {
            'name': '有效URL测试（模拟）',
            'data': {'url': 'https://example.com'},
            'expect_success': False  # 由于网络限制，期望失败但API应正常响应
        },
        {
            'name': '无效URL测试',
            'data': {'url': 'invalid-url'},
            'expect_success': False
        },
        {
            'name': '空URL测试',
            'data': {},
            'expect_success': False
        }
    ]
    
    base_url = 'http://127.0.0.1:5000'
    
    for case in test_cases:
        print(f"\n📝 {case['name']}")
        try:
            response = requests.post(f"{base_url}/api/scrape", 
                                   json=case['data'], 
                                   timeout=10)
            
            print(f"   状态码: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}...")
                
                if case['expect_success']:
                    if result.get('success'):
                        print("   ✅ 测试通过")
                    else:
                        print("   ❌ 预期成功但失败")
                else:
                    if not result.get('success'):
                        print("   ✅ 测试通过（预期失败）")
                    else:
                        print("   ❌ 预期失败但成功")
            else:
                print(f"   响应内容: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 请求异常: {e}")
        except Exception as e:
            print(f"   ❌ 其他异常: {e}")

def test_extract_scrape_command():
    """测试命令提取功能"""
    print("\n🧪 测试网页抓取命令提取...")
    
    # 导入命令提取函数
    sys.path.append('/home/runner/work/chat2/chat2')
    from app import extract_scrape_command
    
    test_messages = [
        ('抓取网页：https://example.com', 'https://example.com'),
        ('爬取网页: https://test.com/page', 'https://test.com/page'),
        ('获取网页信息 https://site.org', 'https://site.org'),
        ('scrape: https://api.example.com', 'https://api.example.com'),
        ('请帮我分析一下 https://news.com/article', 'https://news.com/article'),
        ('这是一个普通消息，没有URL', None),
        ('', None)
    ]
    
    for message, expected in test_messages:
        result = extract_scrape_command(message)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{message[:30]}...' -> {result}")

if __name__ == "__main__":
    print("🚀 开始API测试...")
    
    # 首先测试命令提取功能（不需要启动服务器）
    test_extract_scrape_command()
    
    # 启动Flask应用进行API测试
    flask_process = None
    try:
        flask_process = start_flask_app()
        test_scrape_api()
        print("\n🎉 API测试完成!")
        
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        
    finally:
        # 清理：停止Flask进程
        if flask_process:
            print("\n🛑 停止Flask应用...")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flask_process.kill()
                flask_process.wait()