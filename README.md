# HTTP 渲染桥梁插件

一个 AstrBot 插件，作为外部服务与 QQ 之间的"渲染桥梁"，将结构化的 HTTP 请求数据动态转化为信息清晰、视觉突出的图片。

## 功能特性

- 🌐 **HTTP API 接口** - 提供标准化的 REST API 接收外部请求
- 🔐 **Bearer Token 认证** - 安全的 API 访问控制
- 🎨 **多模板系统** - 支持管理员配置多个 HTML 模板
- 📱 **动态渲染** - 使用 Jinja2 模板引擎动态填充数据
- 🖼️ **本地图片生成** - 强制使用 AstrBot 本地渲染引擎
- � ***样式完整保留** - 直接渲染 HTML，保留所有 CSS 样式和布局
- � **智智能后备机制** - HTML 渲染失败时自动降级为 Markdown 渲染
- 📤 **智能发送** - 支持群聊和私聊消息发送

## 快速开始

### 1. 安装插件

将插件文件放置到 AstrBot 的 `data/plugins/astrbot_plugin_http_render_bridge/` 目录下。

### 2. 配置插件

在 AstrBot 管理面板中找到"HTTP渲染桥梁"插件，进行以下配置：

- **API接口路径**: 自定义 API 访问路径（默认：`/api/render/image`）
- **认证令牌**: 设置 Bearer Token（建议使用强密码）
- **服务地址**: HTTP 服务监听地址（默认：`0.0.0.0:11451`）
- **HTML模板**: 配置多个模板，每个模板需要唯一的别名

### 3. 配置 HTML 模板

插件采用简化的文件化模板管理：

#### 🎨 模板文件管理

插件会自动扫描 `templates/` 目录下的所有 `.html` 文件：

| 模板文件 | 模板名称 | 用途 |
|----------|----------|------|
| `notification.html` | `notification` | 通用通知消息 |
| `alert.html` | `alert` | 警告和错误消息 |
| `success.html` | `success` | 成功和完成消息 |
| `nomination.html` | `nomination` | 提名展示 |
| `report.html` | `report` | 数据报告 |
| `default.html` | `default` | 默认模板 |

#### ⚙️ 全局配置

在AstrBot管理面板中配置全局参数：
- **默认渲染宽度** - 所有模板的默认宽度（像素）
- **默认图片质量** - 所有模板的默认质量（low/medium/high/ultra）

#### 🛠️ 添加自定义模板

只需在 `templates/` 目录下添加新的 `.html` 文件即可：

1. 创建新的HTML文件，如 `custom.html`
2. 插件会自动检测并加载为 `custom` 模板
3. 通过API调用时使用 `X-Html-Template: custom`

#### 📝 模板变量

所有模板都支持Jinja2语法和变量：
```html
{{title | default('默认标题')}}
{{content | default('默认内容')}}
{{message | default('默认消息')}}
{{timestamp | default('刚刚')}}
{{level | default('INFO')}}
```

#### 💡 简化管理优势
- **零配置** - 文件存在即可用，无需额外配置
- **直观命名** - 文件名即模板名，简单明了
- **热加载** - 重启插件后自动检测新模板
- **版本控制友好** - 每个模板都是独立的HTML文件

## API 使用方法

### 请求格式

```http
POST /api/render/image
Authorization: Bearer YOUR_TOKEN
X-Html-Template: notification
X-Target-Type: group
X-Target-Id: 123456789
Content-Type: multipart/form-data

title=系统通知&content=这是一条重要通知&timestamp=2024-01-01 12:00:00
```

**注意**: `X-Html-Template` 参数直接使用HTML文件名（不含.html后缀）

### 请求头说明

| 请求头 | 必需 | 说明 |
|--------|------|------|
| `Authorization` | 是 | Bearer Token 认证 |
| `X-Html-Template` | 是 | 指定使用的模板别名 |
| `X-Target-Type` | 是 | 发送目标类型：`group`（群聊）或 `private`（私聊） |
| `X-Target-Id` | 是 | 发送目标的具体 ID（群号或 QQ 号） |

### 请求体格式

使用 `multipart/form-data` 格式，包含用于填充模板的键值对数据。

### 响应格式

**成功响应 (200)**:
```json
{
    "status": "success",
    "message": "Image sent successfully",
    "template_used": "notification",
    "target": "group:123456789"
}
```

**错误响应**:
```json
{
    "status": "error",
    "message": "Header 'X-Html-Template' is missing"
}
```

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求格式错误（缺少必要头部、模板不存在等） |
| 401 | 认证失败（Token 无效或缺失） |
| 500 | 服务器内部错误（渲染失败、发送失败等） |

## 使用示例

### Python 示例

```python
import requests

url = "http://localhost:11451/api/render/image"
headers = {
    "Authorization": "Bearer your_token_here",
    "X-Html-Template": "notification",
    "X-Target-Type": "group",
    "X-Target-Id": "123456789"
}
data = {
    "title": "系统通知",
    "content": "服务器维护完成",
    "timestamp": "2024-01-01 12:00:00"
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
```

## 本地渲染说明

### 渲染方式

插件现在**强制使用本地渲染**，不再依赖外部网络渲染服务：

1. **HTML 模板处理**: 使用 Jinja2 引擎渲染 HTML 模板
2. **直接 HTML 渲染**: 将完整的 HTML 内容（包含 CSS 样式）直接传递给本地渲染引擎
3. **样式保留**: 完整保留 HTML 模板中的所有 CSS 样式和布局
4. **后备机制**: 如果 HTML 渲染失败，自动降级为 Markdown 渲染
5. **自动发送**: 将生成的图片发送到指定目标

### 优势

- ✅ **无网络依赖**: 完全本地化处理，不需要外部服务
- ✅ **样式完整保留**: HTML 模板的所有 CSS 样式都会被保留
- ✅ **更高稳定性**: 避免网络渲染服务的不稳定性
- ✅ **更快响应**: 本地处理速度更快
- ✅ **更好隐私**: 数据不会发送到外部服务器
- ✅ **智能后备**: HTML 渲染失败时自动使用 Markdown 后备方案

### 注意事项

- 优先使用 HTML 直接渲染，保留所有样式和布局
- 仅在 HTML 渲染失败时才会降级为 Markdown 渲染
- 支持完整的 CSS 样式，包括复杂的布局和动画效果
- 建议在 HTML 模板中使用内联 CSS 以获得最佳兼容性

### curl 示例

```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "Authorization: Bearer your_token_here" \
  -H "X-Html-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=系统通知" \
  -F "content=服务器维护完成" \
  -F "timestamp=2024-01-01 12:00:00"
```

## 模板开发指南

### Jinja2 语法支持

- **变量**: `{{variable_name}}`
- **默认值**: `{{variable_name | default('默认值')}}`
- **条件**: `{% if condition %}...{% endif %}`
- **循环**: `{% for item in items %}...{% endfor %}`

### 最佳实践

1. **响应式设计**: 使用相对单位和媒体查询
2. **字体选择**: 优先使用系统字体
3. **颜色搭配**: 确保良好的对比度
4. **性能优化**: 避免过大的图片和复杂的 CSS

## 健康检查

插件提供健康检查端点：

```http
GET /health
```

返回插件状态信息：
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
        },
        {
            "name": "alert",
            "file": "alert.html", 
            "description": "基于alert.html的模板"
        }
    ],
    "timestamp": "2024-01-01T12:00:00"
}
```

## 故障排除

### 常见问题

1. **模板渲染失败**
   - 检查 Jinja2 语法是否正确
   - 确认所有变量都有提供或设置了默认值

2. **消息发送失败**
   - 确认目标 ID 是否正确
   - 检查 AstrBot 平台适配器是否正常工作

3. **认证失败**
   - 确认 Token 配置正确
   - 检查请求头格式：`Bearer <token>`

### 日志查看

插件会在 AstrBot 日志中输出详细的运行信息，标识为 `[AstrBot Plugin HTTP Render Bridge]`。

## 版本历史

- **v1.0.0** - 初始版本
  - HTTP API 接口
  - 多模板系统
  - 图片渲染功能
  - 消息发送功能

## 许可证

本插件遵循 MIT 许可证。