# HTTP 渲染桥梁插件部署指南

## 环境要求

- AstrBot v3.4.0 或更高版本
- Python 3.8+
- 支持的平台适配器（如 aiocqhttp）

## 安装步骤

### 1. 下载插件

将插件文件放置到 AstrBot 的插件目录：

```bash
# 假设 AstrBot 安装在 /path/to/astrbot
cd /path/to/astrbot/data/plugins/
git clone <plugin-repository> astrbot_plugin_http_render_bridge
```

或者手动创建目录并复制文件：

```bash
mkdir -p /path/to/astrbot/data/plugins/astrbot_plugin_http_render_bridge
# 复制所有插件文件到该目录
```

### 2. 安装依赖

插件依赖会在 AstrBot 启动时自动安装，或者手动安装：

```bash
pip install aiohttp>=3.8.0 jinja2>=3.1.0
```

### 3. 启动 AstrBot

启动 AstrBot，插件会自动加载：

```bash
cd /path/to/astrbot
python main.py
```

### 4. 配置插件

在 AstrBot Web 管理界面中：

1. 进入 **插件管理** 页面
2. 找到 **HTTP渲染桥梁** 插件
3. 点击 **管理** 按钮
4. 配置以下参数：

#### 基础配置

- **API接口路径**: `/api/render/image` (默认)
- **认证令牌**: 设置一个强密码作为 API 访问令牌
- **服务监听地址**: `0.0.0.0` (默认，监听所有接口)
- **服务端口**: `8080` (默认)

#### 模板配置

插件会自动创建默认的 `notification` 模板。你可以：

1. 使用默认模板
2. 修改默认模板
3. 添加新的自定义模板

### 5. 验证安装

#### 检查服务状态

访问健康检查端点：

```bash
curl http://localhost:8080/health
```

预期响应：
```json
{
    "status": "ok",
    "plugin": "astrbot_plugin_http_render_bridge",
    "version": "1.0.0",
    "templates_count": 1,
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 测试 API 调用

使用提供的测试脚本：

```bash
cd /path/to/plugin/astrbot_plugin_http_render_bridge
python test_api.py
```

## 配置详解

### 认证配置

```json
{
    "auth_token": "your_secure_token_here"
}
```

- 如果不设置 `auth_token`，API 将不进行认证验证
- 建议使用强密码，如：`abc123XYZ!@#$%^&*()_+`
- 令牌会在 HTTP 请求头中使用：`Authorization: Bearer <token>`

### 网络配置

```json
{
    "server_host": "0.0.0.0",
    "server_port": 8080,
    "api_path": "/api/render/image"
}
```

- `server_host`: 
  - `0.0.0.0` - 监听所有网络接口
  - `127.0.0.1` - 仅监听本地回环接口
  - 具体 IP - 监听指定网络接口
- `server_port`: HTTP 服务端口，确保端口未被占用
- `api_path`: API 接口路径，可自定义

### 模板配置

每个模板包含以下字段：

```json
{
    "templates": {
        "template_alias": {
            "alias": "template_alias",
            "name": "模板显示名称",
            "description": "模板用途描述",
            "html_content": "HTML模板内容，支持Jinja2语法",
            "render_width": 800,
            "render_quality": "high"
        }
    }
}
```

- `alias`: 模板别名，用于 API 请求中的 `X-Html-Template` 头
- `name`: 模板显示名称，用于管理界面
- `description`: 模板描述，帮助理解模板用途
- `html_content`: HTML 模板内容，支持 Jinja2 语法
- `render_width`: 渲染图片宽度（像素）
- `render_quality`: 图片质量 (`high`/`medium`/`low`)

## 防火墙配置

如果需要外部访问，确保防火墙允许配置的端口：

### Linux (iptables)

```bash
# 允许 8080 端口
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### Linux (ufw)

```bash
# 允许 8080 端口
sudo ufw allow 8080
```

### Windows

在 Windows 防火墙中添加入站规则，允许端口 8080。

## 反向代理配置

### Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api/render/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间，因为图片渲染可能需要较长时间
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### Apache

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyPass /api/render/ http://127.0.0.1:8080/
    ProxyPassReverse /api/render/ http://127.0.0.1:8080/
    
    # 增加超时时间
    ProxyTimeout 30
</VirtualHost>
```

## SSL/HTTPS 配置

如果需要 HTTPS 访问，建议使用反向代理（如 Nginx）处理 SSL 终止：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /api/render/ {
        proxy_pass http://127.0.0.1:8080;
        # ... 其他配置
    }
}
```

## 监控和日志

### 日志位置

插件日志会输出到 AstrBot 的日志系统中，标识为 `[AstrBot Plugin HTTP Render Bridge]`。

### 监控指标

- HTTP 请求数量和响应时间
- 模板渲染成功/失败率
- 消息发送成功/失败率
- 服务器资源使用情况

### 健康检查

定期检查服务状态：

```bash
#!/bin/bash
# health_check.sh
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
if [ $response -eq 200 ]; then
    echo "Service is healthy"
else
    echo "Service is unhealthy (HTTP $response)"
fi
```

## 故障排除

### 常见问题

1. **服务无法启动**
   - 检查端口是否被占用：`netstat -tlnp | grep 8080`
   - 检查 AstrBot 日志中的错误信息

2. **API 请求失败**
   - 验证认证令牌是否正确
   - 检查请求头格式是否正确
   - 确认模板别名是否存在

3. **图片渲染失败**
   - 检查 HTML 模板语法是否正确
   - 验证 Jinja2 变量是否都有提供
   - 查看 AstrBot 日志中的详细错误信息

4. **消息发送失败**
   - 确认 AstrBot 平台适配器正常工作
   - 检查目标群号/用户号是否正确
   - 验证机器人是否有发送权限

### 调试模式

启用详细日志记录：

1. 在 AstrBot 配置中设置日志级别为 `DEBUG`
2. 重启 AstrBot
3. 查看详细的请求和响应日志

### 性能优化

1. **模板缓存**: 插件会自动缓存编译后的模板
2. **图片质量**: 根据需要调整图片质量设置
3. **并发限制**: 如果需要，可以在反向代理中设置并发限制

## 安全建议

1. **使用强认证令牌**: 至少 32 位随机字符
2. **限制网络访问**: 仅允许必要的 IP 地址访问
3. **使用 HTTPS**: 在生产环境中使用 SSL/TLS
4. **定期更新**: 保持插件和依赖库的最新版本
5. **监控日志**: 定期检查访问日志，发现异常访问

## 备份和恢复

### 备份配置

```bash
# 备份插件配置
cp /path/to/astrbot/data/config/astrbot_plugin_http_render_bridge_config.json backup/
```

### 恢复配置

```bash
# 恢复插件配置
cp backup/astrbot_plugin_http_render_bridge_config.json /path/to/astrbot/data/config/
# 重启 AstrBot
```

## 升级指南

1. 停止 AstrBot
2. 备份当前配置
3. 更新插件文件
4. 启动 AstrBot
5. 验证功能正常

插件会自动处理配置文件的版本兼容性。