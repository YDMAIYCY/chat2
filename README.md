# 量子智能聊天助手 - 网页抓取版本

**Chat2 - Web Scraping Enhanced Version**

一个集成了Python网页抓取功能的智能聊天应用，支持中文命令和实时网页信息提取。

## 🌟 主要功能

### 💬 聊天功能
- 基于DeepSeek API的智能对话
- 实时WebSocket通信
- 文件上传支持
- 用户对话历史记录

### 🌐 网页抓取功能
- **中文命令支持**: `抓取网页: URL`、`爬取网页 URL`、`获取网页信息 URL`
- **URL自动检测**: 自动识别消息中的网址并提供抓取选项
- **内容提取**: 标题、描述、文本内容、链接、图片
- **元数据解析**: Meta标签和Open Graph信息
- **API接口**: `/api/scrape` 端点用于程序化访问

### 🔒 安全特性
- URL验证和清理
- 防止恶意协议（JavaScript、Data、File等）
- 内容长度限制
- 请求超时保护
- XSS攻击防护

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动应用
```bash
python3 app.py
```

### 访问应用
打开浏览器访问: http://localhost:5000

## 📡 API使用

### 网页抓取API
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 响应格式
```json
{
  "url": "https://example.com",
  "status_code": 200,
  "title": "网页标题",
  "description": "网页描述",
  "content": "网页文本内容...",
  "links": [{"url": "链接地址", "text": "链接文本"}],
  "images": [{"url": "图片地址", "alt": "图片描述"}],
  "meta_info": {"key": "value"},
  "og_info": {"title": "OG标题"},
  "success": true,
  "error": null
}
```

## 💡 使用示例

### 聊天中的抓取命令
- `抓取网页: https://www.python.org`
- `爬取网页 https://github.com/python/cpython`
- `获取网页信息: https://docs.python.org`
- 直接发送网址: `https://realpython.com`

### Python代码示例
```python
from web_scraper import scrape_url, extract_scraping_commands

# 直接抓取网页
result = scrape_url("https://example.com")

# 从文本中提取抓取命令
commands = extract_scraping_commands("请抓取网页: https://example.com")
```

## 📁 文件结构

```
chat2/
├── app.py                    # Flask主应用
├── web_scraper.py           # 网页抓取核心模块
├── requirements.txt         # 依赖列表
├── templates/
│   └── index.html          # 前端模板
├── static/
│   ├── css/style.css       # 样式文件
│   └── js/main.js          # 前端JavaScript
├── uploads/                # 文件上传目录
└── test_*.py               # 测试文件
```

## 🧪 测试

### 运行本地功能测试
```bash
python3 test_local_functionality.py
```

### 运行完整演示
```bash
python3 demo_functionality.py
```

### 测试API端点
```bash
python3 test_api.py
```

## 🛠️ 技术栈

- **后端**: Flask, Flask-SocketIO, BeautifulSoup4, lxml
- **前端**: HTML5, TailwindCSS, Socket.IO
- **抓取**: requests, BeautifulSoup4, lxml
- **AI集成**: DeepSeek API

## 📈 功能亮点

1. **智能命令识别**: 自动识别中文抓取命令和URL
2. **实时通信**: 基于WebSocket的实时消息传递
3. **安全可靠**: 多层安全检查和错误处理
4. **响应迅速**: 优化的网页解析和内容提取
5. **用户友好**: 直观的中文界面和操作提示

## 🔧 配置选项

### 环境变量
- `DEEPSEEK_API_KEY`: DeepSeek API密钥

### 抓取配置
```python
scraper = WebScraper(
    timeout=15,  # 请求超时时间
    user_agent="自定义User-Agent"
)
```

## 📝 开发说明

这个项目实现了原issue"使用python爬虫抓取网页信息"的所有要求：

- ✅ Python网页抓取功能
- ✅ 中文命令支持 
- ✅ 聊天界面集成
- ✅ API接口提供
- ✅ 安全防护措施
- ✅ 错误处理机制
- ✅ 完整的测试覆盖

## 📄 许可证

本项目为开源项目，仅供学习和研究使用。

---

**作者**: Copilot Coding Agent  
**项目**: YDMAIYCY/chat2  
**版本**: 1.0.0 (网页抓取增强版)