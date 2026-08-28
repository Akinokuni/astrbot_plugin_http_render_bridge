# HTTP 渲染桥梁插件部署指南

## 环境要求

- AstrBot v3.4.0 或更高版本
- Python 3.8+
- 支持的平台适配器（如 aiocqhttp）
- Typst 渲染引擎（二选一，推荐安装 Python 绑定）：
  - 官方 `typst` Python 绑定（`pip install typst`），内存编译，主渲染路径
  - 系统安装 `typst` CLI，作为后备渲染路径
- 中文字体：无需安装。插件捆绑 Noto Sans SC 与 LXGW WenKai Lite 中文字体（`fonts/` 目录），通过 `TYPST_FONT_PATHS` 环境变量挂载，无系统字体环境也能正常渲染中文

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
pip install aiohttp>=3.8.0 typst>=0.13.0
```

推荐同时安装 Typst CLI 作为后备渲染路径（可选）：

```bash
# Windows: 下载 typst.exe 并加入 PATH（https://github.com/typst/typst/releases）
# macOS: brew install typst
# Linux: cargo install --locked typst-cli
# 或下载预编译二进制放入 /usr/local/bin/

# 验证安装
typst --version
```

> 渲染引擎优先级：官方 `typst` Python 绑定（内存编译）→ `typst` CLI 子进程。绑定不可用时自动回退 CLI，两者都缺失时模板模式不可用（直接消息模式不受影响）。

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

插件会自动创建默认的 `notification` 模板（`notification.typ`）。你可以：

1. 使用默认模板
2. 修改默认模板
3. 在 `templates/` 目录下添加新的 `.typ` 模板文件
4. 通过配置 JSON 添加自定义模板（`typ_content` 字段）

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
            "typ_content": "Typst模板内容，通过 sys.inputs.at(\"data\") 读取注入数据",
            "render_quality": "high"
        }
    }
}
```

- `alias`: 模板别名，用于 API 请求中的 `X-Template` 头
- `name`: 模板显示名称，用于管理界面
- `description`: 模板描述，帮助理解模板用途
- `typ_content`: Typst 模板内容（模板开头需读取 `sys.inputs.at("data")`）
- `render_quality`: 图片质量 (`ultra`/`high`/`medium`/`low`，映射 300/200/144/72 PPI)

> 模板文件也可以直接以 `.typ` 文件形式放在插件的 `templates/` 目录下，文件名即模板别名。

### 字体配置

#### 内置中文字体

插件捆绑以下轻量中文字体（`fonts/` 目录），随插件分发：

| 字体文件 | Typst 字体族名 | 风格 |
|----------|---------------|------|
| `NotoSansSC-Regular.ttf` | Noto Sans SC | 现代黑体 |
| `LXGWWenKaiLite-Regular.ttf` | LXGW WenKai Lite | 手写楷体 |

插件初始化时将 `fonts/` 目录挂载到 `TYPST_FONT_PATHS` 环境变量（typst CLI 自动读取该变量扫描字体），官方 Python 绑定在编译时通过 `font_paths` 参数显式传入同一目录。环境中已存在的 `TYPST_FONT_PATHS` 值被保留并拼接在后。两条渲染路径均无需系统字体即可命中捆绑字体。

#### 在线字体缓存

```json
{
    "font_cache_dir": "font_cache",
    "font_download_timeout": 30
}
```

- `font_cache_dir`: 在线字体缓存目录。相对路径基于插件目录解析，绝对路径按原样使用。模板声明的字体下载后存放于此。
- `font_download_timeout`: 单个字体下载超时（秒）。

在线字体 URL 在模板内部以 `// @font-url` 注释声明（每行一个 URL），HTTP 请求不携带字体参数。插件渲染时提取声明，异步下载至缓存目录并即时挂载到字体扫描路径。缓存文件名取 URL 的 SHA-256 摘要，同一 URL 只下载一次，后续渲染直接命中缓存离线编译。

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
   - 检查 Typst 模板语法是否正确
   - 验证模板开头是否读取了 `sys.inputs.at("data")`
   - 确认已安装 `typst` Python 包或 CLI（`pip show typst` / `typst --version`）
   - 查看 AstrBot 日志中 Typst 错误信息（含精确行列号）

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

1. **渲染引擎**: 优先使用 `typst` Python 绑定（内存编译，无进程启动开销）；CLI 后备模式性能略低
2. **PPI 档位**: 根据需要调整图片质量设置（72/144/200/300 PPI）
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