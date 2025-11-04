# API 参考文档

本文档详细描述了 AstrBot HTTP 渲染桥梁插件的所有 API 接口。

## 📋 基本信息

- **基础URL**: `http://localhost:11451` (默认)
- **API路径**: `/api/render/image` (默认)
- **协议**: HTTP/HTTPS
- **内容类型**: `multipart/form-data`

## 🔧 通用请求头

### 必需请求头

| 请求头 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `X-Target-Type` | string | 目标类型 | `group` 或 `private` |
| `X-Target-Id` | string | 目标ID | 群号或QQ号 |

### 可选请求头

| 请求头 | 类型 | 说明 | 默认值 |
|--------|------|------|-------|
| `X-Message-Type` | string | 消息类型 | `template` |
| `X-Html-Template` | string | HTML模板名 | 仅模板模式需要 |
| `Authorization` | string | Bearer Token认证 | 可选 |

## 🎯 API 端点

### 1. 主要消息接口

#### POST /api/render/image

发送消息的主要接口，支持两种模式：

1. **HTML模板渲染模式** (默认)
2. **直接消息发送模式**

**请求格式:**
```http
POST /api/render/image
Content-Type: multipart/form-data
X-Target-Type: group
X-Target-Id: 123456789
X-Message-Type: text

text=Hello, World!
```

**响应格式:**
```json
{
    "status": "success",
    "message": "Text message sent successfully",
    "message_type": "text",
    "target": "group:123456789"
}
```

### 2. 健康检查接口

#### GET /health

检查插件状态和可用模板。

**请求:**
```http
GET /health
```

**响应:**
```json
{
    "status": "ok",
    "plugin": "astrbot_plugin_http_render_bridge",
    "version": "1.0.0",
    "templates_count": 6,
    "available_templates": [
        {
            "name": "notification",
            "file": "notification.html",
            "description": "基于notification.html的模板"
        }
    ],
    "timestamp": "2024-10-30T18:00:00.000Z"
}
```

## 📝 消息类型详细说明

### HTML模板渲染 (template)

**请求头:**
```
X-Html-Template: notification
# X-Message-Type 不设置或设置为 template
```

**参数:** 根据模板需要

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=系统通知" \
  -F "content=这是一条通知消息"
```

### 纯文本消息 (text)

**请求头:**
```
X-Message-Type: text
```

**参数:**
- `text` (string, 必需) - 消息文本内容
- `content` (string, 可选) - 消息内容的别名

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: text" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=Hello, World!"
```

### 图片消息 (image)

**请求头:**
```
X-Message-Type: image
```

**参数:**
- `image` (file, 可选) - 图片文件
- `url` (string, 可选) - 图片URL

**支持格式:** JPG, PNG, GIF, WebP, BMP
**大小限制:** 5MB

**示例:**
```bash
# 上传文件
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "image=@photo.jpg"

# 使用URL
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "url=https://example.com/image.jpg"
```

### @用户消息 (at)

**请求头:**
```
X-Message-Type: at
```

**参数:**
- `qq` (string, 必需) - 要@的用户QQ号，`all` 表示@全体
- `user_id` (string, 可选) - `qq` 的别名
- `text` (string, 可选) - 附加文本

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

### 回复消息 (reply)

**请求头:**
```
X-Message-Type: reply
```

**参数:**
- `message_id` (string, 必需) - 要回复的消息ID
- `id` (string, 可选) - `message_id` 的别名
- `text` (string, 可选) - 回复内容
- `content` (string, 可选) - `text` 的别名

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: reply" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "message_id=12345" \
  -F "text=我同意你的观点"
```

### 表情消息 (face)

**请求头:**
```
X-Message-Type: face
```

**参数:**
- `face_id` (string, 必需) - QQ表情ID
- `id` (string, 可选) - `face_id` 的别名

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: face" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "face_id=1"
```

### 链接分享 (share)

**请求头:**
```
X-Message-Type: share
```

**参数:**
- `url` (string, 必需) - 分享链接
- `title` (string, 可选) - 分享标题
- `content` (string, 可选) - 分享描述
- `description` (string, 可选) - `content` 的别名
- `image` (string, 可选) - 分享图片URL

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: share" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "url=https://github.com/example" \
  -F "title=GitHub项目" \
  -F "content=一个很棒的开源项目"
```

### 音乐分享 (music)

**请求头:**
```
X-Message-Type: music
```

**参数:**
- `id` (string, 必需) - 音乐ID
- `type` (string, 可选) - 音乐平台 (`163`=网易云, `qq`=QQ音乐, `xm`=虾米)

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: music" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "type=163" \
  -F "id=12345678"
```

### 位置分享 (location)

**请求头:**
```
X-Message-Type: location
```

**参数:**
- `lat` (string, 必需) - 纬度
- `latitude` (string, 可选) - `lat` 的别名
- `lon` (string, 必需) - 经度
- `longitude` (string, 可选) - `lon` 的别名
- `title` (string, 可选) - 位置标题
- `content` (string, 可选) - 位置描述
- `address` (string, 可选) - `content` 的别名

**示例:**
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: location" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "lat=39.9042" \
  -F "lon=116.4074" \
  -F "title=天安门广场"
```

### 混合消息 (mixed)

**请求头:**
```
X-Message-Type: mixed
```

**参数:**
- `text` (string, 可选) - 文本内容
- `content` (string, 可选) - `text` 的别名
- `image` (file, 可选) - 图片文件
- `at` (string, 可选) - 要@的用户QQ号

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

## 📊 响应格式

### 成功响应

**状态码:** 200

**格式:**
```json
{
    "status": "success",
    "message": "操作成功描述",
    "message_type": "消息类型",
    "target": "目标信息",
    "template_used": "使用的模板名(仅模板模式)"
}
```

### 错误响应

**状态码:** 400, 401, 500

**格式:**
```json
{
    "status": "error",
    "message": "错误描述"
}
```

### 常见错误码

| 状态码 | 说明 | 可能原因 |
|--------|------|----------|
| 400 | 请求参数错误 | 缺少必需参数、参数格式错误 |
| 401 | 认证失败 | Token无效或缺失 |
| 500 | 服务器内部错误 | 渲染失败、发送失败 |

## 🔐 认证机制

### Bearer Token 认证

如果配置了 `auth_token`，需要在请求头中包含：

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

### 跳过认证

如果未配置 `auth_token`，则跳过认证检查。

## 📏 限制和约束

### 文件大小限制

- **图片文件**: 最大 5MB
- **语音文件**: 遵循NapCat限制
- **视频文件**: 遵循NapCat限制

### 支持的文件格式

- **图片**: JPG, JPEG, PNG, GIF, WebP, BMP
- **语音**: MP3, WAV, AMR等
- **视频**: MP4, AVI等

### 请求频率

无特殊限制，但建议合理控制请求频率以避免被QQ限制。

## 🧪 测试工具

### cURL 示例

```bash
# 测试健康检查
curl -X GET http://localhost:11451/health

# 发送文本消息
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: text" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=测试消息"

# 使用认证
curl -X POST http://localhost:11451/api/render/image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Message-Type: text" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=认证测试"
```

### Python 示例

```python
import requests

# 基本配置
BASE_URL = "http://localhost:11451"
API_PATH = "/api/render/image"
TOKEN = "your_token_here"  # 可选

def send_message(message_type, target_type, target_id, data=None, files=None):
    """发送消息的通用函数"""
    url = f"{BASE_URL}{API_PATH}"
    headers = {
        "X-Message-Type": message_type,
        "X-Target-Type": target_type,
        "X-Target-Id": target_id
    }
    
    # 添加认证头（如果需要）
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    response = requests.post(url, headers=headers, data=data, files=files)
    return response.json()

# 使用示例
result = send_message("text", "group", "123456789", {"text": "Hello!"})
print(result)
```

## 🔍 调试技巧

### 1. 检查插件状态

```bash
curl -X GET http://localhost:11451/health
```

### 2. 查看日志

插件会在AstrBot日志中记录详细的处理过程。

### 3. 验证参数

确保所有必需参数都已提供，参数名称正确。

### 4. 测试连接

先测试简单的文本消息，确认基本功能正常。

---

## 📚 相关文档

- [消息类型详细指南](MESSAGE_TYPES_GUIDE.md)
- [HTML模板开发指南](HTML_TEMPLATE_GUIDE.md)
- [图片上传功能指南](IMAGE_UPLOAD_GUIDE.md)
- [部署和配置指南](DEPLOYMENT.md)