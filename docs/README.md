# AstrBot HTTP 渲染桥梁插件 - 文档中心

欢迎来到 AstrBot HTTP 渲染桥梁插件的文档中心！这里包含了插件的完整使用指南和开发文档。

## 文档目录

### 快速开始

- [**README.md**](../README.md) - 项目概述和快速开始指南
- [**部署指南**](DEPLOYMENT.md) - 详细的安装和部署说明

### 功能指南

- [**Typst模板书写指南**](TYPST_TEMPLATE_GUIDE.md) - 创建美观Typst模板的完整指南
- [**图片上传功能指南**](IMAGE_UPLOAD_GUIDE.md) - 图片上传和处理功能使用说明
- [**NapCat消息类型指南**](MESSAGE_TYPES_GUIDE.md) - 支持的15种消息类型详细说明
- [**模板配置指南**](TEMPLATE_CONFIG_GUIDE.md) - 模板系统配置和管理

### 测试和开发

- [**测试指南**](TESTING_GUIDE.md) - 插件测试方法和工具
- [**API参考**](API_REFERENCE.md) - 完整的API接口文档
- [**更新日志**](CHANGELOG.md) - 版本更新记录

## 功能概览

### 核心功能

1. **Typst模板渲染** - 将动态数据编译为美观的 PNG 图片
2. **图片上传支持** - 支持多种格式图片的上传和处理
3. **二维码生成** - 自动生成二维码并嵌入模板
4. **内置中文字体** - 捆绑 Noto Sans SC 与 LXGW WenKai Lite，通过 `TYPST_FONT_PATHS` 挂载，无系统字体环境也能渲染中文
5. **在线字体扩展** - 外部字体 URL 异步下载至 `font_cache/` 缓存并即时挂载到字体扫描路径
6. **NapCat消息类型** - 支持15种不同的消息类型直接发送
7. **多平台兼容** - 支持群聊和私聊消息发送

### 支持的消息类型

- **模板渲染**: Typst模板 → PNG图片 → 消息
- **直接消息**: 文本、图片、语音、视频、@用户、回复、转发等
- **特殊消息**: 表情、戳一戳、抖动、音乐分享、链接分享、位置分享
- **混合消息**: 文本+图片+@用户的组合消息

## 技术架构

```
HTTP请求 → 插件处理 → 消息构建 → NapCat → QQ
    ↓
[模板渲染] 或 [直接消息]
    ↓
Typst编译→PNG 或 消息数据
```

渲染引擎：优先官方 `typst` Python 绑定（内存编译），自动回退 `typst` CLI 子进程。

## 使用场景

### 1. 系统通知
```bash
# Typst模板渲染
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=系统维护通知" \
  -F "content=服务器将在今晚进行维护"
```

### 2. 数据报告
```bash
# 使用报告模板
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Template: report" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=每日数据报告" \
  -F "total_users=1000" \
  -F "active_users=800"
```

### 3. 图片分享
```bash
# 直接发送图片
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: image" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "image=@photo.jpg"
```

### 4. 链接分享
```bash
# 分享链接卡片
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Message-Type: share" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "url=https://github.com/example" \
  -F "title=GitHub项目"
```

## 模板示例

### 通知模板
- 适用于系统通知、公告发布
- 支持标题、内容、时间戳
- 可选二维码和图片

### 报告模板
- 适用于数据展示、统计报告
- 支持多项数据指标
- 网格布局，清晰易读

### 提名模板
- 适用于评选、投票活动
- 支持多项提名展示
- 专业的视觉设计

### 图片展示模板
- 适用于图片集合展示
- 支持单图和多图布局
- Typst 网格布局

## 相关链接

- [GitHub仓库](https://github.com/Akinokuni/astrbot_plugin_http_render_bridge)
- [AstrBot官网](https://astrbot.app)
- [NapCat文档](https://napcat.napneko.icu)

## 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看相关文档是否有解决方案
2. 在GitHub仓库提交Issue
3. 参与社区讨论

---

**提示**: 建议按照文档顺序阅读，从部署指南开始，然后根据需要查看具体功能指南。