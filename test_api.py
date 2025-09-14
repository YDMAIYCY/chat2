#!/usr/bin/env python3
"""
Test the web scraping API endpoint
测试网页抓取API接口
"""

import requests
import json
import time
import threading
import subprocess
import sys

def start_flask_app():
    """Start the Flask application in a separate process"""
    import os
    os.chdir('/home/runner/work/chat2/chat2')
    subprocess.run([sys.executable, 'app.py'])

def test_api_endpoint():
    """Test the /api/scrape endpoint"""
    print("测试 /api/scrape API 接口")
    print("=" * 40)
    
    # Test API endpoint
    api_url = "http://localhost:5000/api/scrape"
    
    test_cases = [
        {
            "name": "有效网址测试",
            "url": "https://httpbin.org/html",
            "expected_success": True
        },
        {
            "name": "无效网址测试",
            "url": "not-a-valid-url",
            "expected_success": False
        },
        {
            "name": "空网址测试",
            "url": "",
            "expected_success": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试案例: {test_case['name']}")
        print(f"网址: {test_case['url']}")
        
        try:
            response = requests.post(
                api_url, 
                json={"url": test_case['url']},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"抓取成功: {data.get('success', False)}")
                if data.get('success'):
                    print(f"标题: {data.get('title', 'N/A')}")
                    print(f"描述: {data.get('description', 'N/A')[:100]}...")
                else:
                    print(f"错误: {data.get('error', 'N/A')}")
            else:
                try:
                    error_data = response.json()
                    print(f"API错误: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"响应错误: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("无法连接到Flask应用，请确保服务器正在运行")
        except Exception as e:
            print(f"测试异常: {str(e)}")

def test_homepage():
    """Test if the homepage loads correctly"""
    print("\n测试主页加载")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"主页HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("主页加载成功")
            # Check if the page contains our scraping instructions
            if "网页抓取功能" in response.text:
                print("✅ 网页包含抓取功能说明")
            else:
                print("❌ 网页缺少抓取功能说明")
        else:
            print(f"主页加载失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到Flask应用")
    except Exception as e:
        print(f"主页测试异常: {str(e)}")

if __name__ == "__main__":
    print("API接口测试脚本")
    print("=" * 50)
    
    print("注意：请先在另一个终端中运行 'python3 app.py' 启动服务器")
    input("服务器启动后，按回车键开始测试...")
    
    # Wait a moment for the server to be ready
    time.sleep(2)
    
    test_homepage()
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("API测试完成！")