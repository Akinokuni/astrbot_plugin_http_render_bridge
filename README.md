# HTTP 渲染桥梁插件

一个 AstrBot 插件，作为外部服务与 QQ 之间的"渲染桥梁"，将结构化的 HTTP 请求数据动态转化为信息清晰、视觉突出的图片。

## 功能特性

- 🌐 **HTTP API 接口** - 提供标准化的 REST API 接收外部请求
- 🔐 **Bearer Token 认证** - 安全的 API 访问控制
- 🎨 **多模板系统** - 支持管理员配置多个 HTML 模板
- 📱 **动态渲染** - 使用 Jinja2 模板引擎动态填充数据
- 🖼️ **图片生成** - 将 HTML 渲染为高质量图片
- 📤 **智能发送** - 支持群聊和私聊消息发送

## 快速开始

### 1. 安装插件

将插件文件放置到 AstrBot 的 `data/plugins/astrbot_plugin_http_render_bridge/` 目录下。

### 2. 配置插件

在 AstrBot 管理面板中找到"HTTP渲染桥梁"插件，进行以下配置：

- **API接口路径**: 自定义 API 访问路径（默认：`/api/render/image`）
- **认证令牌**: 设置 Bearer Token（建议使用强密码）
- **服务地址**: HTTP 服务监听地址（默认：`0.0.0.0:8080`）
- **HTML模板**: 配置多个模板，每个模板需要唯一的别名

### 3. 配置 HTML 模板

插件提供了用户友好的配置界面，无需手写JSON配置：

#### 🎨 预设模板
- **通知模板** (`notification`) - 蓝色渐变背景的通用通知
- **警告模板** (`alert`) - 红色主题的警告消息  
- **成功模板** (`success`) - 绿色主题的成功消息

#### 🛠️ 自定义模板
支持最多3个自定义模板，每个模板独立配置：
- **启用开关** - 一键启用/禁用模板
- **别名设置** - API调用时使用的标识符
- **显示名称** - 管理界面显示的友好名称
- **HTML编辑** - 完整的HTML/CSS编辑器
- **渲染设置** - 宽度和质量配置

#### 📝 模板变量
所有模板都支持以下Jinja2变量：
```html
{{title | default('默认标题')}}
{{content | default('默认内容')}}
{{message | default('默认消息')}}
{{timestamp | default('刚刚')}}
{{level | default('INFO')}}
```

#### ⚙️ 配置优势
- **无需编程** - 通过表单界面轻松配置
- **即时预览** - 每个配置项都有详细说明
- **灵活控制** - 可以随时启用/禁用任何模板
- **简单管理** - 不再需要手写复杂的JSON配置

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

url = "http://localhost:8080/api/render/image"
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

### curl 示例

```bash
curl -X POST http://localhost:8080/api/render/image \
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
    "templates_count": 3,
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