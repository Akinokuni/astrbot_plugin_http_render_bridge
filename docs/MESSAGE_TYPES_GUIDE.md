# NapCat 消息类型支持指南

本指南介绍如何使用 AstrBot HTTP 渲染桥梁插件发送各种类型的 NapCat 消息。

## 📋 功能概述

插件现在支持两种工作模式：

1. **HTML模板渲染模式**（默认）- 传统的HTML模板渲染功能
2. **直接消息发送模式** - 直接发送各种NapCat消息类型

## 🎯 使用方法

### 模式选择

通过 `X-Message-Type` 请求头来选择消息类型：

- **不设置** 或 **设置为 `template`** - 使用HTML模板渲染
- **设置为其他值** - 直接发送对应类型的消息

### 基本请求格式

```http
POST /api/render/image
X-Message-Type: text
X-Target-Type: group
X-Target-Id: 123456789
Content-Type: multipart/form-data

text=你好，这是一条测试消息
```

## 📝 支持的消息类型

### 1. 纯文本消息 (`text`)

发送纯文本消息。

**请求头:**
```
X-Message-Type: text
```

**参数:**
- `text` 或 `content` - 消息文本内容

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: text" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=这是一条纯文本消息"
```

### 2. 图片消息 (`image`)

发送图片消息。

**请求头:**
```
X-Message-Type: image
```

**参数:**
- `image` - 图片文件（multipart上传）
- `url` - 图片URL地址

**示例:**
```bash
# 上传图片文件
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "image=@photo.jpg"

# 使用图片URL
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "url=https://example.com/image.jpg"
```

### 3. 语音消息 (`voice`)

发送语音消息。

**请求头:**
```
X-Message-Type: voice
```

**参数:**
- `voice` - 语音文件（multipart上传）
- `url` - 语音文件URL

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: voice" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "voice=@audio.mp3"
```

### 4. 视频消息 (`video`)

发送视频消息。

**请求头:**
```
X-Message-Type: video
```

**参数:**
- `video` - 视频文件（multipart上传）
- `url` - 视频文件URL

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: video" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "video=@movie.mp4"
```

### 5. @用户消息 (`at`)

发送@用户的消息。

**请求头:**
```
X-Message-Type: at
```

**参数:**
- `qq` 或 `user_id` - 要@的用户QQ号，使用 `all` 表示@全体成员
- `text` - 附加的文本内容（可选）

**示例:**
```bash
# @特定用户
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: at" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "qq=987654321" \
  -F "text=你好！"

# @全体成员
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: at" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "qq=all" \
  -F "text=大家好！"
```

### 6. 回复消息 (`reply`)

回复特定消息。

**请求头:**
```
X-Message-Type: reply
```

**参数:**
- `message_id` 或 `id` - 要回复的消息ID
- `text` 或 `content` - 回复内容

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: reply" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "message_id=12345" \
  -F "text=我同意你的观点"
```

### 7. 转发消息 (`forward`)

转发特定消息。

**请求头:**
```
X-Message-Type: forward
```

**参数:**
- `message_id` 或 `id` - 要转发的消息ID

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: forward" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "message_id=12345"
```

### 8. 表情消息 (`face`)

发送QQ表情。

**请求头:**
```
X-Message-Type: face
```

**参数:**
- `face_id` 或 `id` - QQ表情ID

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: face" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "face_id=1"
```

### 9. 戳一戳 (`poke`)

发送戳一戳。

**请求头:**
```
X-Message-Type: poke
```

**参数:**
- `qq` 或 `user_id` - 要戳的用户QQ号

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: poke" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "qq=987654321"
```

### 10. 窗口抖动 (`shake`)

发送窗口抖动（仅私聊有效）。

**请求头:**
```
X-Message-Type: shake
```

**参数:**
无需参数

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: shake" \
  -H "X-Target-Type: private" \
  -H "X-Target-Id: 987654321"
```

### 11. 音乐分享 (`music`)

分享音乐。

**请求头:**
```
X-Message-Type: music
```

**参数:**
- `type` - 音乐平台类型（`163`=网易云音乐, `qq`=QQ音乐, `xm`=虾米音乐）
- `id` - 音乐ID

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: music" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "type=163" \
  -F "id=12345678"
```

### 12. 链接分享 (`share`)

分享链接。

**请求头:**
```
X-Message-Type: share
```

**参数:**
- `url` - 链接地址（必需）
- `title` - 分享标题（可选）
- `content` 或 `description` - 分享描述（可选）
- `image` - 分享图片URL（可选）

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: share" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "url=https://github.com/Akinokuni/astrbot_plugin_http_render_bridge" \
  -F "title=AstrBot插件" \
  -F "content=HTTP渲染桥梁插件" \
  -F "image=https://github.com/fluidicon.png"
```

### 13. 位置分享 (`location`)

分享地理位置。

**请求头:**
```
X-Message-Type: location
```

**参数:**
- `lat` 或 `latitude` - 纬度（必需）
- `lon` 或 `longitude` - 经度（必需）
- `title` - 位置标题（可选）
- `content` 或 `address` - 位置描述（可选）

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: location" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "lat=39.9042" \
  -F "lon=116.4074" \
  -F "title=天安门广场" \
  -F "content=北京市东城区"
```

### 14. 混合消息 (`mixed`)

发送包含多种元素的混合消息。

**请求头:**
```
X-Message-Type: mixed
```

**参数:**
- `text` 或 `content` - 文本内容（可选）
- `image` - 图片文件（可选）
- `at` - 要@的用户QQ号（可选）

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: mixed" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=看看这张图片" \
  -F "image=@photo.jpg" \
  -F "at=987654321"
```

### 15. HTML模板渲染 (`template` 或不设置)

传统的HTML模板渲染功能。

**请求头:**
```
X-Html-Template: notification
# X-Message-Type 不设置或设置为 template
```

**参数:**
根据模板需要的参数

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=系统通知" \
  -F "content=这是一条HTML模板渲染的消息"
```

## 🔧 Python 示例

### 基本用法

```python
import requests

def send_text_message(text, target_type='group', target_id='123456789'):
    """发送文本消息"""
    url = "http://localhost:11451/api/render/image"
    headers = {
        "X-Message-Type": "text",
        "X-Target-Type": target_type,
        "X-Target-Id": target_id
    }
    data = {"text": text}
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def send_at_message(qq, text, target_type='group', target_id='123456789'):
    """发送@消息"""
    url = "http://localhost:11451/api/render/image"
    headers = {
        "X-Message-Type": "at",
        "X-Target-Type": target_type,
        "X-Target-Id": target_id
    }
    data = {"qq": qq, "text": text}
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def send_image_message(image_path, target_type='group', target_id='123456789'):
    """发送图片消息"""
    url = "http://localhost:11451/api/render/image"
    headers = {
        "X-Message-Type": "image",
        "X-Target-Type": target_type,
        "X-Target-Id": target_id
    }
    
    with open(image_path, 'rb') as f:
        files = {"image": f}
        response = requests.post(url, headers=headers, files=files)
    
    return response.json()

# 使用示例
result = send_text_message("Hello, World!")
print(result)

result = send_at_message("987654321", "你好！")
print(result)

result = send_image_message("photo.jpg")
print(result)
```

### 高级用法

```python
class NapCatMessageSender:
    def __init__(self, base_url="http://localhost:11451", api_path="/api/render/image"):
        self.base_url = base_url
        self.api_path = api_path
    
    def _send_request(self, message_type, target_type, target_id, data=None, files=None):
        """发送请求的通用方法"""
        url = f"{self.base_url}{self.api_path}"
        headers = {
            "X-Message-Type": message_type,
            "X-Target-Type": target_type,
            "X-Target-Id": target_id
        }
        
        response = requests.post(url, headers=headers, data=data, files=files)
        return response.json()
    
    def send_text(self, text, target_type='group', target_id='123456789'):
        """发送文本消息"""
        return self._send_request('text', target_type, target_id, {'text': text})
    
    def send_share(self, url, title=None, content=None, image=None, target_type='group', target_id='123456789'):
        """发送链接分享"""
        data = {'url': url}
        if title:
            data['title'] = title
        if content:
            data['content'] = content
        if image:
            data['image'] = image
        
        return self._send_request('share', target_type, target_id, data)
    
    def send_mixed(self, text=None, image_path=None, at_qq=None, target_type='group', target_id='123456789'):
        """发送混合消息"""
        data = {}
        files = {}
        
        if text:
            data['text'] = text
        if at_qq:
            data['at'] = at_qq
        if image_path:
            files['image'] = open(image_path, 'rb')
        
        try:
            return self._send_request('mixed', target_type, target_id, data, files)
        finally:
            # 关闭文件
            for f in files.values():
                if hasattr(f, 'close'):
                    f.close()

# 使用示例
sender = NapCatMessageSender()

# 发送文本
sender.send_text("Hello, World!")

# 发送链接分享
sender.send_share(
    url="https://github.com/Akinokuni/astrbot_plugin_http_render_bridge",
    title="AstrBot插件",
    content="HTTP渲染桥梁插件"
)

# 发送混合消息
sender.send_mixed(
    text="看看这张图片",
    image_path="photo.jpg",
    at_qq="987654321"
)
```

## 📋 响应格式

### 成功响应

```json
{
    "status": "success",
    "message": "Text message sent successfully",
    "message_type": "text",
    "target": "group:123456789"
}
```

### 错误响应

```json
{
    "status": "error",
    "message": "Missing X-Target-Type or X-Target-Id header"
}
```

## ❓ 常见问题

### Q: 如何保持向后兼容性？

A: 不设置 `X-Message-Type` 头或设置为 `template` 时，插件会使用传统的HTML模板渲染功能。

### Q: 支持哪些文件格式？

A: 
- 图片：JPG, PNG, GIF, WebP, BMP
- 语音：MP3, WAV, AMR等（取决于NapCat支持）
- 视频：MP4, AVI等（取决于NapCat支持）

### Q: 文件大小限制是多少？

A: 图片文件限制5MB，其他文件类型遵循NapCat的限制。

### Q: 如何调试消息发送？

A: 查看插件日志，所有消息构建和发送过程都会记录详细日志。

### Q: 支持群聊和私聊吗？

A: 是的，通过 `X-Target-Type` 头指定：
- `group` - 群聊
- `private` - 私聊

## 🚀 最佳实践

1. **错误处理**: 始终检查响应状态码和消息
2. **文件管理**: 及时关闭上传的文件句柄
3. **参数验证**: 发送前验证必需参数
4. **日志监控**: 关注插件日志以便调试
5. **兼容性**: 保持对旧版本API的兼容性

---

## 📚 相关文档

- [NapCat消息格式文档](https://napcat.napneko.icu/develop/msg)
- [HTML模板书写指南](HTML_TEMPLATE_GUIDE.md)
- [图片上传功能指南](IMAGE_UPLOAD_GUIDE.md)
- [插件部署指南](DEPLOYMENT.md)

---

**提示**: 这个功能完全向后兼容，现有的HTML模板渲染功能不受影响。