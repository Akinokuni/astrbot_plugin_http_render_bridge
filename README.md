# AstrBot HTTP 渲染桥梁插件

一个功能强大的 AstrBot 插件，提供 HTTP API 接口，支持 HTML 模板渲染、图片上传、二维码生成和多种 NapCat 消息类型的发送。

## 🎯 功能特性

### 核心功能
- 🌐 **HTTP API 接口** - 提供标准化的 REST API 接收外部请求
- 🔐 **Bearer Token 认证** - 安全的 API 访问控制
- 🎨 **双模式支持** - HTML模板渲染 + 直接消息发送
- 📱 **动态渲染** - 使用 Jinja2 模板引擎动态填充数据

### HTML模板功能
- 🖼️ **本地图片生成** - 强制使用 AstrBot 本地渲染引擎
- 💎 **样式完整保留** - 直接渲染 HTML，保留所有 CSS 样式和布局
- 🔄 **智能后备机制** - HTML 渲染失败时自动降级为 Markdown 渲染
- 📸 **图片上传支持** - 支持多种格式图片上传和嵌入
- 🔗 **二维码生成** - 自动生成二维码并嵌入模板

### NapCat消息类型
- 📝 **15种消息类型** - 支持文本、图片、语音、视频等
- 👥 **@用户消息** - 支持@特定用户或@全体成员
- 🔄 **回复转发** - 支持消息回复和转发功能
- 😀 **表情互动** - 支持QQ表情、戳一戳、窗口抖动
- 🎵 **媒体分享** - 支持音乐、链接、位置分享
- 🎭 **混合消息** - 支持文本+图片+@用户的组合消息

### 技术特性
- 📤 **智能发送** - 支持群聊和私聊消息发送
- 🔧 **零配置模板** - 文件化模板管理，即放即用
- 🚀 **高性能处理** - 内存处理，无磁盘IO
- 📊 **完整监控** - 健康检查和详细日志

## 🚀 快速开始

### 1. 安装插件

将插件文件放置到 AstrBot 的 `data/plugins/astrbot_plugin_http_render_bridge/` 目录下。

### 2. 配置插件

在 AstrBot 管理面板中配置插件：

```json
{
  "api_path": "/api/render/image",
  "auth_token": "your_secure_token_here",
  "server_host": "0.0.0.0",
  "server_port": 11451
}
```

### 3. 使用示例

#### HTML模板渲染
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=系统通知" \
  -F "content=这是一条重要通知"
```

#### 直接发送文本消息
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: text" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "text=Hello, World!"
```

#### 发送图片消息
```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "image=@photo.jpg"
```

## 📋 支持的消息类型

| 类型 | 说明 | 示例用途 |
|------|------|----------|
| `template` | HTML模板渲染（默认） | 系统通知、数据报告 |
| `text` | 纯文本消息 | 简单文本发送 |
| `image` | 图片消息 | 图片分享 |
| `voice` | 语音消息 | 语音播报 |
| `video` | 视频消息 | 视频分享 |
| `at` | @用户消息 | 提醒特定用户 |
| `reply` | 回复消息 | 回复特定消息 |
| `forward` | 转发消息 | 消息转发 |
| `face` | 表情消息 | QQ表情发送 |
| `poke` | 戳一戳 | 互动功能 |
| `shake` | 窗口抖动 | 私聊提醒 |
| `music` | 音乐分享 | 音乐推荐 |
| `share` | 链接分享 | 网页分享 |
| `location` | 位置分享 | 地理位置 |
| `mixed` | 混合消息 | 复合内容 |

## 🎨 内置模板

| 模板名 | 文件 | 用途 |
|--------|------|------|
| `notification` | notification.html | 通用通知消息 |
| `alert` | alert.html | 警告和错误消息 |
| `success` | success.html | 成功和完成消息 |
| `nomination` | nomination.html | 提名展示 |
| `report` | report.html | 数据报告 |
| `image_showcase` | image_showcase.html | 图片展示 |
| `default` | default.html | 默认模板 |

## 📝 API 接口

### 主要端点

- **POST** `/api/render/image` - 发送消息（模板渲染或直接发送）
- **GET** `/health` - 健康检查

### 请求头

| 请求头 | 必需 | 说明 |
|--------|------|------|
| `X-Message-Type` | 否 | 消息类型，默认为 `template` |
| `X-Html-Template` | 条件 | HTML模板名（模板模式必需） |
| `X-Target-Type` | 是 | 目标类型：`group` 或 `private` |
| `X-Target-Id` | 是 | 目标ID（群号或QQ号） |
| `Authorization` | 否 | Bearer Token认证 |

### 响应格式

```json
{
    "status": "success",
    "message": "操作成功描述",
    "message_type": "消息类型",
    "target": "目标信息"
}
```

## 🖼️ 图片上传功能

### 支持格式
- JPG, JPEG, PNG, GIF, WebP, BMP
- 最大文件大小：5MB
- 自动转换为base64嵌入模板

### 使用方法
```bash
# 在模板中显示图片
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=图片通知" \
  -F "content=包含图片的消息" \
  -F "image=@photo.jpg"

# 直接发送图片
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "image=@photo.jpg"
```

## 🔗 二维码功能

### 自动生成
传入 `link` 参数，插件会自动生成二维码并显示在模板右上角：

```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=扫码访问" \
  -F "content=请扫描右上角二维码" \
  -F "link=https://github.com/example" \
  -F "qr_text=扫码查看项目"
```

## 🐍 Python SDK

```python
import requests

class AstrBotMessageSender:
    def __init__(self, base_url="http://localhost:11451", token=None):
        self.base_url = base_url
        self.token = token
    
    def send_template(self, template, target_type, target_id, **data):
        """发送HTML模板消息"""
        headers = {
            "X-Html-Template": template,
            "X-Target-Type": target_type,
            "X-Target-Id": target_id
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = requests.post(
            f"{self.base_url}/api/render/image",
            headers=headers,
            data=data
        )
        return response.json()
    
    def send_text(self, text, target_type, target_id):
        """发送文本消息"""
        headers = {
            "X-Message-Type": "text",
            "X-Target-Type": target_type,
            "X-Target-Id": target_id
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = requests.post(
            f"{self.base_url}/api/render/image",
            headers=headers,
            data={"text": text}
        )
        return response.json()

# 使用示例
sender = AstrBotMessageSender(token="your_token")

# 发送模板消息
sender.send_template(
    template="notification",
    target_type="group",
    target_id="123456789",
    title="系统通知",
    content="这是一条测试消息"
)

# 发送文本消息
sender.send_text("Hello, World!", "group", "123456789")
```

## 📚 文档

详细文档请查看 [docs](docs/) 目录：

- [📖 文档中心](docs/README.md) - 完整文档索引
- [🚀 部署指南](docs/DEPLOYMENT.md) - 安装和配置说明
- [🎨 HTML模板指南](docs/HTML_TEMPLATE_GUIDE.md) - 模板开发指南
- [📸 图片上传指南](docs/IMAGE_UPLOAD_GUIDE.md) - 图片功能使用说明
- [📝 消息类型指南](docs/MESSAGE_TYPES_GUIDE.md) - NapCat消息类型详解
- [🔧 API参考](docs/API_REFERENCE.md) - 完整API文档
- [🧪 测试指南](docs/TESTING_GUIDE.md) - 测试方法和工具

## 🔧 配置选项

```json
{
  "api_path": "/api/render/image",
  "auth_token": "your_secure_token_here",
  "server_host": "0.0.0.0",
  "server_port": 11451
}
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `api_path` | string | `/api/render/image` | API接口路径 |
| `auth_token` | string | `""` | Bearer Token认证 |
| `server_host` | string | `0.0.0.0` | 服务监听地址 |
| `server_port` | int | `11451` | 服务端口 |

## 🧪 测试工具

项目包含多个测试脚本：

- `test_message_types.py` - 测试各种消息类型
- `test_image_upload.py` - 测试图片上传功能
- `test_qr_code.py` - 测试二维码生成
- `test_templates.py` - 测试HTML模板渲染

```bash
# 运行测试
python test_message_types.py
python test_image_upload.py
```

## 🔍 故障排除

### 常见问题

1. **连接失败**
   - 检查服务是否启动：`curl http://localhost:11451/health`
   - 确认端口配置正确

2. **认证失败**
   - 检查Token配置：`Authorization: Bearer your_token`
   - 确认Token格式正确

3. **模板渲染失败**
   - 检查模板文件是否存在
   - 验证Jinja2语法正确性

4. **消息发送失败**
   - 确认目标ID正确
   - 检查AstrBot平台连接状态

### 日志查看

插件日志标识为 `[AstrBot Plugin HTTP Render Bridge]`，包含详细的处理过程信息。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个插件！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [AstrBot](https://astrbot.app) - 主项目
- [NapCat](https://napcat.napneko.icu) - QQ机器人框架
- [Jinja2](https://jinja.palletsprojects.com/) - 模板引擎

---

**⭐ 如果这个插件对你有帮助，请给个Star支持一下！**