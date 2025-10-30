# HTTP 渲染桥梁插件开发计划

## 项目概述
开发一个 AstrBot 插件，作为外部服务与 QQ 之间的"渲染桥梁"，将结构化的 HTTP 请求数据动态转化为信息清晰、视觉突出的图片。

## 核心功能需求

### 1. HTTP API 接口
- [x] 提供 POST 接口，支持自定义路径
- [x] Bearer Token 认证机制
- [x] 支持 multipart/form-data 请求体
- [x] 自定义请求头控制：
  - `X-Html-Template`: 指定 HTML 模板别名
  - `X-Target-Type`: 发送目标类型 (group/private)
  - `X-Target-Id`: 发送目标 ID
- [x] 完整的错误处理和响应

### 2. HTML 模板管理
- [x] 支持多个 HTML 模板配置
- [x] 模板别名系统
- [x] Jinja2 模板引擎支持 {{占位符}}
- [x] 模板渲染参数配置（宽度、质量等）

### 3. 后台管理界面
- [x] API 接口路径配置
- [x] 认证令牌管理
- [x] HTML 模板 CRUD 操作
- [x] 模板编辑器（支持代码高亮）
- [x] 渲染参数配置

### 4. 图片渲染与发送
- [x] HTML 转图片渲染
- [x] 支持多平台发送
- [x] 错误处理和日志记录

## 开发任务清单

### Phase 1: 项目结构搭建
- [x] 创建插件基础文件结构
- [x] 配置 metadata.yaml
- [x] 设计配置 schema (_conf_schema.json)
- [x] 创建 requirements.txt

### Phase 2: 核心 HTTP 服务
- [x] 实现 HTTP 服务器 (aiohttp)
- [x] 请求认证中间件
- [x] 请求头验证
- [x] multipart/form-data 解析
- [x] 错误处理和响应

### Phase 3: 模板系统
- [x] 模板存储和管理
- [x] Jinja2 模板渲染
- [x] 模板别名映射
- [x] 默认模板创建

### Phase 4: 图片渲染
- [x] 集成 AstrBot html_render 功能
- [x] 渲染参数配置
- [x] 错误处理

### Phase 5: 消息发送
- [x] 平台适配器集成
- [x] 群聊/私聊发送支持
- [x] 发送错误处理

### Phase 6: 配置管理
- [x] 后台配置界面设计
- [x] 模板管理界面
- [x] 配置验证

### Phase 7: 测试与优化
- [x] 单元测试
- [x] 集成测试
- [x] 性能优化
- [x] 文档编写

## 技术栈
- **Web 框架**: aiohttp
- **模板引擎**: Jinja2
- **图片渲染**: AstrBot html_render (Playwright)
- **配置管理**: AstrBot 配置系统
- **认证**: Bearer Token

## 文件结构
```
http_render_bridge/
├── main.py                 # 主插件文件
├── metadata.yaml          # 插件元数据
├── requirements.txt       # 依赖包
├── _conf_schema.json     # 配置 schema
├── templates/            # HTML 模板目录
│   └── default.html      # 默认模板
└── README.md            # 插件说明文档
```

## 开发进度
- [x] 需求分析完成
- [x] 技术方案确定
- [x] 参考项目分析完成
- [ ] 开始编码实现

## 下一步行动
1. 创建插件基础文件结构
2. 实现配置 schema 设计
3. 开发 HTTP 服务核心功能
4. 实现模板管理系统
5. 集成图片渲染功能