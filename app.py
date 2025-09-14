from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import requests
import json
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
from web_scraper import WebScraper, extract_scraping_commands, scrape_from_text

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, async_mode='threading')

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize web scraper
web_scraper = WebScraper(timeout=15)

# 配置DeepSeek API信息
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'Bearer sk-ab5b18ee8d9646aa89d14811f29bd156')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 存储对话历史
user_conversations = {}


# 主页路由
@app.route('/')
def index():
    return render_template('index.html')


# 文件上传路由
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        # 生成唯一文件名防止冲突
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        logger.info(f"文件上传成功: {filename}")
        return jsonify({'status': True, 'file': filename})
    logger.warning("文件上传失败: 未提供文件")
    return jsonify({'status': False})


# WebSocket消息处理
@socketio.on('send_message')
def handle_message(data):
    """处理客户端发送的消息"""
    logger.info(f"收到客户端消息: {data}")

    # 提取消息内容
    user_id = data.get('user_id')
    message = data.get('message')
    files = data.get('files', [])

    if not message and not files:
        logger.warning("收到空消息")
        return

    # 异步调用AI API获取回复
    socketio.start_background_task(get_ai_response, user_id, message, files)


# 获取AI回复
def get_ai_response(user_id, message, files=[]):
    """调用DeepSeek API获取AI回复"""
    try:
        # Check for web scraping commands first
        scraping_commands = extract_scraping_commands(message)
        
        if scraping_commands:
            logger.info(f"检测到网页抓取命令: {len(scraping_commands)}个")
            
            # Process scraping commands
            scraping_results = []
            for cmd in scraping_commands:
                result = web_scraper.extract_content(cmd['url'])
                scraping_results.append(result)
            
            # Format scraping results
            scraping_response = format_scraping_results(scraping_results)
            
            # Send scraping results to client
            socketio.emit('receive_message', {
                'user_id': user_id,
                'message': message,
                'reply': scraping_response,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'scraping'
            })
            
            logger.info(f"网页抓取完成并发送结果")
            return
        
        # 构建完整的消息内容，包括文件信息
        full_message = message
        if files:
            file_list = "\n\n用户上传了以下文件:"
            for file in files:
                file_list += f"\n- {file['name']}"
            full_message += file_list

        # 获取或创建用户对话历史
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # 添加用户消息到对话历史
        user_conversations[user_id].append({"role": "user", "content": full_message})

        # 准备API请求
        headers = {
            "Authorization": DEEPSEEK_API_KEY,
            "Content-Type": "application/json"
        }

        # 构建包含对话历史的消息列表
        messages = user_conversations[user_id]

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        logger.info(f"调用DeepSeek API: {DEEPSEEK_API_URL}")

        # 发送请求
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            response_data = response.json()
            ai_reply = response_data.get('choices', [{}])[0].get('message', {}).get('content',
                                                                                    '抱歉，我无法回答这个问题')

            # 添加AI回复到对话历史
            user_conversations[user_id].append({"role": "assistant", "content": ai_reply})

            # 发送回复给客户端
            socketio.emit('receive_message', {
                'user_id': user_id,
                'message': message,
                'reply': ai_reply,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            logger.info(f"AI回复成功: {ai_reply[:50]}...")

        else:
            error_msg = f"API请求失败: {response.status_code}, 详情: {response.text}"
            logger.error(error_msg)

            # 发送错误信息给客户端
            socketio.emit('receive_message', {
                'user_id': user_id,
                'message': message,
                'reply': '抱歉，暂时无法获取AI回复',
                'error': error_msg,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        logger.error(error_msg)

        # 发送错误信息给客户端
        socketio.emit('receive_message', {
            'user_id': user_id,
            'message': message,
            'reply': '请检查网络连接是否正常',
            'error': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        error_msg = f"处理异常: {str(e)}"
        logger.error(error_msg)

        # 发送错误信息给客户端
        socketio.emit('receive_message', {
            'user_id': user_id,
            'message': message,
            'reply': '系统错误，请稍后重试',
            'error': error_msg,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })


def format_scraping_results(results):
    """Format scraping results for display"""
    if not results:
        return "没有找到可抓取的内容。"
    
    formatted_results = []
    
    for result in results:
        if result['success']:
            formatted_result = f"""
🌐 **网页抓取结果**

**网址**: {result['url']}
**标题**: {result['title']}
**描述**: {result['description']}

**内容摘要**:
{result['content'][:300]}{'...' if len(result['content']) > 300 else ''}

**链接数量**: {len(result['links'])}
**图片数量**: {len(result['images'])}
"""
            if result['og_info']:
                formatted_result += f"\n**Open Graph信息**:\n"
                for key, value in result['og_info'].items():
                    formatted_result += f"- {key}: {value}\n"
        else:
            formatted_result = f"""
❌ **抓取失败**

**网址**: {result['url']}
**错误**: {result['error']}
"""
        
        formatted_results.append(formatted_result)
    
    return "\n" + "="*50 + "\n".join(formatted_results) + "="*50


# API聊天接口（备选方案）
@app.route('/api/chat', methods=['POST'])
def chat():
    """直接通过API获取AI回复的接口"""
    user_input = request.json.get('message')
    user_id = request.json.get('user_id', 'default_user')
    if not user_input:
        return jsonify({'reply': '请输入内容', 'error': '消息不能为空'}), 400

    try:
        # 获取或创建用户对话历史
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # 添加用户消息到对话历史
        user_conversations[user_id].append({"role": "user", "content": user_input})

        # 准备API请求
        headers = {
            "Authorization": DEEPSEEK_API_KEY,
            "Content-Type": "application/json"
        }

        # 构建包含对话历史的消息列表
        messages = user_conversations[user_id]

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024
        }

        logger.info(f"调用DeepSeek API: {DEEPSEEK_API_URL}")

        # 发送请求
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            response_data = response.json()
            ai_reply = response_data.get('choices', [{}])[0].get('message', {}).get('content',
                                                                                    '抱歉，我无法回答这个问题')

            # 添加AI回复到对话历史
            user_conversations[user_id].append({"role": "assistant", "content": ai_reply})

            return jsonify({'reply': ai_reply})

        else:
            error_msg = f"API请求失败: {response.status_code}, 详情: {response.text}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'reply': '抱歉，暂时无法获取AI回复'
            }), 500

    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'error': error_msg,
            'reply': '请检查网络连接是否正常'
        }), 500

    except Exception as e:
        error_msg = f"处理异常: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'error': error_msg,
            'reply': '系统错误，请稍后重试'
        }), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_webpage():
    """API endpoint for web scraping"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL参数是必需的'
            }), 400
        
        logger.info(f"API请求抓取网页: {url}")
        
        # Scrape the webpage
        result = web_scraper.extract_content(url)
        
        logger.info(f"API抓取完成: {url}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"API抓取异常: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


if __name__ == '__main__':
    logger.info("启动量子智能聊天助手服务器...")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5000)