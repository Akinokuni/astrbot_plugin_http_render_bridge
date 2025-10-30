# HTTP渲染桥梁插件 - 测试指南

## 🎯 测试准备

### 1. 确认环境
- ✅ AstrBot已启动并运行
- ✅ HTTP渲染桥梁插件已安装并启用
- ✅ Docker环境正常（如果使用Docker）

### 2. 插件配置
在AstrBot管理面板中配置以下参数：

| 配置项 | 建议值 | 说明 |
|--------|--------|------|
| API接口路径 | `/api/render/image` | 默认值 |
| 认证令牌 | `test_token_123` | 测试用令牌 |
| 服务监听地址 | `0.0.0.0` | 监听所有接口 |
| 服务端口 | `11451` | 默认端口 |
| 默认渲染宽度 | `800` | 像素 |
| 默认图片质量 | `high` | 高质量 |

## 🧪 测试步骤

### 第一步：健康检查测试

```bash
python test_health.py
```

**预期结果**：
```
🚀 HTTP渲染桥梁插件 - 健康检查测试
==================================================
🏥 测试健康检查端点
🔗 请求地址: http://localhost:11451/health
📥 响应状态: 200
✅ 服务健康!
📊 插件信息:
   - 插件名称: astrbot_plugin_http_render_bridge
   - 版本: 1.0.0
   - 模板数量: 6
   - 时间戳: 2024-01-01T12:00:00

📋 可用模板 (6个):
   - notification (notification.html): 基于notification.html的模板
   - alert (alert.html): 基于alert.html的模板
   - success (success.html): 基于success.html的模板
   - nomination (nomination.html): 基于nomination.html的模板
   - report (report.html): 基于report.html的模板
   - default (default.html): 基于default.html的模板

🎉 健康检查通过! 可以开始API测试
```

### 第二步：模板渲染测试

```bash
python test_templates.py
```

**预期结果**：
每个模板都应该返回成功响应：
```
🧪 测试模板: notification
📤 发送数据: {'title': '系统通知', 'content': '这是一条测试通知消息...'}
📥 响应状态: 200
📄 响应内容: {"status": "success", "message": "Image sent successfully", "template_used": "notification", "target": "group:123456789"}
✅ 测试成功!
```

### 第三步：手动API测试

使用curl命令测试单个模板：

```bash
# 测试通知模板
curl -X POST http://localhost:11451/api/render/image \\
  -H "Authorization: Bearer test_token_123" \\
  -H "X-Html-Template: notification" \\
  -H "X-Target-Type: group" \\
  -H "X-Target-Id: 123456789" \\
  -F "title=手动测试" \\
  -F "content=这是手动API测试消息" \\
  -F "timestamp=$(date)"
```

## 🔍 故障排除

### 常见问题

#### 1. 连接失败 (Connection Error)
**症状**: `❌ 连接失败: 无法连接到服务器`

**解决方案**:
- 检查AstrBot是否正常运行
- 确认插件已启用且无错误
- 检查端口11451是否被占用
- 查看AstrBot日志中的错误信息

#### 2. 认证失败 (401 Unauthorized)
**症状**: `📥 响应状态: 401`

**解决方案**:
- 检查认证令牌是否正确配置
- 确认测试脚本中的AUTH_TOKEN与配置一致
- 如果不需要认证，将配置中的认证令牌留空

#### 3. 模板不存在 (400 Bad Request)
**症状**: `Template 'xxx' not found`

**解决方案**:
- 检查templates目录下是否有对应的HTML文件
- 确认文件名拼写正确
- 重启插件以重新扫描模板文件

#### 4. 渲染失败 (500 Internal Server Error)
**症状**: `Failed to render template to image`

**解决方案**:
- 检查HTML模板语法是否正确
- 确认Jinja2变量语法无误
- 查看AstrBot日志中的详细错误信息
- 检查系统是否支持HTML渲染功能

## 📊 测试检查清单

### 基础功能测试
- [ ] 健康检查端点正常响应
- [ ] 显示正确的模板数量
- [ ] 列出所有可用模板

### 模板渲染测试
- [ ] notification模板渲染成功
- [ ] alert模板渲染成功
- [ ] success模板渲染成功
- [ ] nomination模板渲染成功
- [ ] report模板渲染成功
- [ ] default模板渲染成功

### API功能测试
- [ ] Bearer Token认证正常工作
- [ ] 请求头验证正确
- [ ] 表单数据解析正常
- [ ] 错误处理机制有效

### 消息发送测试
- [ ] 群聊消息发送成功
- [ ] 私聊消息发送成功
- [ ] 图片正确生成和发送

## 🎯 性能测试

### 并发测试
```bash
# 使用ab工具进行并发测试
ab -n 100 -c 10 -H "Authorization: Bearer test_token_123" \\
   -H "X-Html-Template: notification" \\
   -H "X-Target-Type: group" \\
   -H "X-Target-Id: 123456789" \\
   http://localhost:11451/api/render/image
```

### 负载测试
```bash
# 使用wrk工具进行负载测试
wrk -t12 -c400 -d30s \\
    -H "Authorization: Bearer test_token_123" \\
    -H "X-Html-Template: notification" \\
    http://localhost:11451/health
```

## 📝 测试报告模板

```
# HTTP渲染桥梁插件测试报告

## 测试环境
- AstrBot版本: [版本号]
- 插件版本: 1.0.0
- 测试时间: [日期时间]
- 测试人员: [姓名]

## 测试结果
### 健康检查: ✅/❌
### 模板加载: ✅/❌ ([数量]个模板)
### API功能: ✅/❌
### 消息发送: ✅/❌

## 发现问题
1. [问题描述]
2. [问题描述]

## 建议改进
1. [改进建议]
2. [改进建议]
```

---

## 🚀 开始测试

现在可以按照上述步骤开始测试了！建议按顺序执行：

1. **健康检查** → `python test_health.py`
2. **模板测试** → `python test_templates.py`
3. **手动验证** → 使用curl命令
4. **功能确认** → 检查QQ群/私聊中的图片消息

祝测试顺利！🎉