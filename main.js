// 聊天功能
const chatBox = document.getElementById('chat-box');
const input = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const fileUpload = document.getElementById('file-upload');
const uploadProgress = document.getElementById('upload-progress');
const progressBar = document.getElementById('progress-bar');

// 存储已上传的文件
let uploadedFiles = [];

// 连接WebSocket
const socket = io('http://localhost:5000');

// 发送消息
sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keypress', e => {
  if (e.key === 'Enter') sendMessage();
});

// 发送文件
fileUpload.addEventListener('change', handleFileUpload);

function sendMessage() {
  const msg = input.value.trim();

  // 如果没有消息内容和上传的文件，不发送
  if (!msg && uploadedFiles.length === 0) return;

  // 构建包含文本和文件的消息
  const messageData = {
    user_id: 'user123',
    message: msg,
    files: uploadedFiles
  };

  // 添加用户消息
  appendMessage('你', msg, 'user');

  // 添加已上传的文件
  uploadedFiles.forEach(file => {
    appendFileMessage('你', file, 'user');
  });

  // 清空输入和已上传文件
  input.value = '';
  uploadedFiles = [];

  // 显示"正在输入"状态
  showTypingIndicator();

  // 通过WebSocket发送消息到服务器
  socket.emit('send_message', messageData);
}

// 处理文件上传
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // 显示进度条
  uploadProgress.classList.remove('hidden');
  progressBar.style.width = '0%';

  // 创建表单数据
  const formData = new FormData();
  formData.append('file', file);

  // 发送文件
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);

  // 监听上传进度
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percentComplete = (e.loaded / e.total) * 100;
      progressBar.style.width = percentComplete + '%';
    }
  });

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      uploadProgress.classList.add('hidden');
      fileUpload.value = ''; // 重置文件输入

      if (xhr.status === 200) {
        try {
          const data = JSON.parse(xhr.responseText);
          if (data.status) {
            // 文件上传成功，保存文件信息
            const fileInfo = {
              type: 'file',
              name: file.name,
              url: `/uploads/${data.file}`
            };

            uploadedFiles.push(fileInfo);

            // 更新输入框提示
            updateInputPlaceholder();
          } else {
            appendMessage('系统', '文件上传失败，请重试', 'system');
          }
        } catch (error) {
          appendMessage('系统', '文件上传出错，请稍后重试', 'system');
          console.error('解析响应失败:', error);
        }
      } else {
        appendMessage('系统', `文件上传失败 (${xhr.status})`, 'system');
        console.error('文件上传错误:', xhr.statusText);
      }
    }
  };

  xhr.send(formData);
}

// 更新输入框提示
function updateInputPlaceholder() {
  if (uploadedFiles.length > 0) {
    input.placeholder = `已选择 ${uploadedFiles.length} 个文件，输入消息并按回车发送...`;
  } else {
    input.placeholder = '输入消息并按回车发送...';
  }
}

// 接收服务器消息
socket.on('receive_message', (data) => {
  hideTypingIndicator();

  // 添加AI回复
  appendMessage('量子AI', data.reply, 'ai');

  if (data.error) {
    console.error('Error from server:', data.error);
    // 可以选择显示错误消息给用户
  }
});

// 添加消息到聊天框
function appendMessage(sender, text, cls) {
  const isUser = cls === 'user';
  const bubbleClass = isUser
    ? 'bg-gradient-to-r from-secondary to-primary text-white rounded-2xl rounded-br-none shadow-lg shadow-secondary/20'
    : 'bg-glass text-light/90 rounded-2xl rounded-bl-none shadow-lg shadow-primary/20';
  const icon = isUser
    ? '<i class="fa fa-user text-secondary"></i>'
    : '<i class="fa fa-robot text-primary"></i>';
  const senderClass = isUser ? 'text-secondary/90' : 'text-primary/70';

  const div = document.createElement('div');
  div.className = `chat-bubble ${cls} max-w-[80%] ${isUser ? 'ml-auto' : ''} animate-float`;
  div.innerHTML = `
    <div class="flex items-start ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'} space-x-3">
      <div class="w-8 h-8 rounded-full ${isUser ? 'bg-secondary/30' : 'bg-primary/30'} flex items-center justify-center">
        ${icon}
      </div>
      <div>
        <div class="text-xs ${senderClass} mb-1">${sender}</div>
        <p class="leading-relaxed">${escapeHtml(text)}</p>
      </div>
    </div>
  `;

  chatBox.appendChild(div);
  scrollToBottom();
}

// 添加文件消息
function appendFileMessage(sender, fileInfo, cls) {
  const isUser = cls === 'user';
  const bubbleClass = isUser
    ? 'bg-gradient-to-r from-secondary to-primary text-white rounded-2xl rounded-br-none shadow-lg shadow-secondary/20'
    : 'bg-glass text-light/90 rounded-2xl rounded-bl-none shadow-lg shadow-primary/20';
  const icon = isUser
    ? '<i class="fa fa-user text-secondary"></i>'
    : '<i class="fa fa-robot text-primary"></i>';
  const senderClass = isUser ? 'text-secondary/90' : 'text-primary/70';

  // 确定文件图标
  let fileIcon = 'fa-file-o';
  if (fileInfo.name.endsWith('.pdf')) fileIcon = 'fa-file-pdf-o';
  else if (fileInfo.name.endsWith('.doc') || fileInfo.name.endsWith('.docx')) fileIcon = 'fa-file-word-o';
  else if (fileInfo.name.endsWith('.txt')) fileIcon = 'fa-file-text-o';
  else if (fileInfo.name.endsWith('.jpg') || fileInfo.name.endsWith('.jpeg') || fileInfo.name.endsWith('.png') || fileInfo.name.endsWith('.gif')) fileIcon = 'fa-file-image-o';

  const div = document.createElement('div');
  div.className = `chat-bubble ${cls} max-w-[80%] ${isUser ? 'ml-auto' : ''} animate-float`;

  // 如果是图片文件，显示预览
  if (fileInfo.name.match(/\.(jpg|jpeg|png|gif|bmp)$/i)) {
    div.innerHTML = `
      <div class="flex items-start ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'} space-x-3">
        <div class="w-8 h-8 rounded-full ${isUser ? 'bg-secondary/30' : 'bg-primary/30'} flex items-center justify-center">
          ${icon}
        </div>
        <div>
          <div class="text-xs ${senderClass} mb-1">${sender}</div>
          <div class="bg-dark/40 p-3 rounded-xl">
            <div class="flex items-center mb-2">
              <i class="fa ${fileIcon} text-primary mr-2"></i>
              <span class="font-medium">${fileInfo.name}</span>
            </div>
            <img src="${fileInfo.url}" alt="上传的图片" class="max-w-full h-auto rounded-lg border border-primary/20">
            <a href="${fileInfo.url}" download="${fileInfo.name}" class="inline-block mt-2 text-sm text-primary hover:underline">
              <i class="fa fa-download mr-1"></i> 下载
            </a>
          </div>
        </div>
      </div>
    `;
  } else {
    // 非图片文件，显示文件链接
    div.innerHTML = `
      <div class="flex items-start ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'} space-x-3">
        <div class="w-8 h-8 rounded-full ${isUser ? 'bg-secondary/30' : 'bg-primary/30'} flex items-center justify-center">
          ${icon}
        </div>
        <div>
          <div class="text-xs ${senderClass} mb-1">${sender}</div>
          <div class="bg-dark/40 p-3 rounded-xl">
            <div class="flex items-center">
              <i class="fa ${fileIcon} text-primary mr-2 text-2xl"></i>
              <div>
                <div class="font-medium">${fileInfo.name}</div>
                <a href="${fileInfo.url}" download="${fileInfo.name}" class="text-sm text-primary hover:underline">
                  <i class="fa fa-download mr-1"></i> 下载文件
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  chatBox.appendChild(div);
  scrollToBottom();
}

// 显示"正在输入"状态
function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.id = 'typing-indicator';
  typingDiv.className = 'chat-bubble ai bg-glass rounded-2xl rounded-bl-none shadow-lg shadow-primary/20 max-w-[40%] animate-float';
  typingDiv.innerHTML = `
    <div class="flex items-start space-x-3">
      <div class="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">
        <i class="fa fa-robot text-primary"></i>
      </div>
      <div>
        <div class="text-xs text-primary/70 mb-1">量子AI</div>
        <div class="flex space-x-1">
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse" style="animation-delay: 0.2s"></div>
          <div class="w-2 h-2 rounded-full bg-primary animate-pulse" style="animation-delay: 0.4s"></div>
        </div>
      </div>
    </div>
  `;

  chatBox.appendChild(typingDiv);
  scrollToBottom();
}

// 隐藏"正在输入"状态
function hideTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

// 滚动到底部
function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

// 防止XSS简单转义
function escapeHtml(text) {
  return text.replace(/[&<>"']/g, m => {
    switch (m) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      case "'": return '&#39;';
    }
  });
}

// 粒子效果
const particlesContainer = document.getElementById('particles');
const numParticles = 60;
const particles = [];

function random(min, max) {
  return Math.random() * (max - min) + min;
}

// 创建粒子
function createParticles() {
  particlesContainer.innerHTML = '';
  particles.length = 0;
  
  for (let i = 0; i < numParticles; i++) {
    const p = document.createElement('div');
    p.classList.add('particle');
    p.style.width = p.style.height = random(3, 10) + 'px';
    p.style.top = random(0, window.innerHeight) + 'px';
    p.style.left = random(0, window.innerWidth) + 'px';
    
    // 随机颜色（紫色到粉色范围）
    const hue = random(260, 320);
    const opacity = random(0.1, 0.4);
    p.style.background = `hsla(${hue}, 100%, 80%, ${opacity})`;
    
    // 不同的动画
    const animations = ['float', 'float', 'float-slow', 'float-fast'];
    const animationDuration = random(8, 15);
    p.style.animation = `${animations[Math.floor(random(0, animations.length))]} ${animationDuration}s ease-in-out infinite`;
    p.style.animationDelay = `${random(0, 5)}s`;
    
    particlesContainer.appendChild(p);
    particles.push(p);
  }
}

// 初始化粒子
createParticles();

// 窗口大小改变时重新定位粒子
window.addEventListener('resize', () => {
  particles.forEach(p => {
    p.style.left = random(0, window.innerWidth) + 'px';
    p.style.top = random(0, window.innerHeight) + 'px';
  });
});

// 鼠标移动时粒子跟随效果（可选）
let mouseX = 0, mouseY = 0;
window.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

setInterval(() => {
  particles.forEach((p, index) => {
    const dx = mouseX - parseFloat(p.style.left);
    const dy = mouseY - parseFloat(p.style.top);
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    if (distance < 200) {
      const force = 0.5 / distance;
      p.style.left = (parseFloat(p.style.left) + dx * force) + 'px';
      p.style.top = (parseFloat(p.style.top) + dy * force) + 'px';
    }
  });
}, 30);