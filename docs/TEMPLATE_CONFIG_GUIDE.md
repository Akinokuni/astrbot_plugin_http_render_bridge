# HTTP渲染桥梁插件 - 模板配置详细教程

## 目录
1. [配置概述](#配置概述)
2. [内置模板配置](#内置模板配置)
3. [自定义模板配置](#自定义模板配置)
4. [模板示例详解](#模板示例详解)
5. [变量使用指南](#变量使用指南)
6. [样式设计技巧](#样式设计技巧)
7. [常见问题解答](#常见问题解答)

## 配置概述

HTTP渲染桥梁插件使用 Typst 作为模板渲染引擎，支持两种模板配置方式：
- **内置模板**：预设的通知模板（`.typ` 文件），可直接使用
- **自定义模板**：通过 JSON 配置添加多个自定义模板

### 渲染引擎说明

插件将 Typst 模板编译为 PNG 图片：

| 渲染路径 | 说明 |
|----------|------|
| **主路径** | 官方 `typst` Python 绑定（`pip install typst`），内存编译，速度快 |
| **后备路径** | 系统安装的 `typst` CLI，Python 绑定不可用时自动回退 |

## 内置模板配置

### 模板文件位置

内置模板以 `.typ` 文件形式存放于插件的 `templates/` 目录：

```
templates/
├── notification.typ    # 通用通知
├── alert.typ           # 警告和错误
├── success.typ         # 成功消息
├── nomination.typ      # 提名展示
├── report.typ          # 数据报告
├── image_showcase.typ  # 图片展示
├── quiz.typ            # 答题结果
└── default.typ         # 默认模板
```

### 质量档位与 PPI 映射

| 档位 | PPI | 适用场景 |
|------|-----|----------|
| `low` | 72 | 快速预览 |
| `medium` | 144 | 常规发送 |
| `high` | 200 | 推荐使用 |
| `ultra` | 300 | 重要场合、大图展示 |

> 输出像素宽度 = 页面宽度(pt) / 72 × PPI。例如模板页面宽 600pt、`high` 档输出 1667px 宽的图片。

## 自定义模板配置

### JSON配置格式

在`自定义模板配置`字段中，输入 JSON 格式的模板配置：

```json
{
  "nomination": {
    "name": "提名模板",
    "description": "用于展示提名信息的模板",
    "typ_content": "#let data = json(bytes(sys.inputs.at(\"data\", default: \"{}\")))\n...",
    "render_quality": "high"
  },
  "report": {
    "name": "报告模板",
    "description": "数据报告展示模板",
    "typ_content": "#let data = json(bytes(sys.inputs.at(\"data\", default: \"{}\")))\n...",
    "render_quality": "ultra"
  }
}
```

### 配置字段说明

每个自定义模板包含以下字段：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 模板显示名称 |
| `description` | string | 否 | 模板描述信息 |
| `typ_content` | string | 是 | 完整的 Typst 模板内容 |
| `render_quality` | string | 否 | 图片质量：low/medium/high/ultra，默认 `high` |

> 版式宽度由模板内的 `#set page(width: ...)` 控制，不通过配置字段设置。

## 模板示例详解

### 提名模板（Typst）

以下是一个完整的提名模板配置示例：

```json
{
  "nomination": {
    "name": "十二器提名模板",
    "description": "用于展示提名信息的精美模板",
    "typ_content": "#let data = json.decode(sys.inputs.at(\"data\", default: \"{}\"))\n#let header = data.at(\"header\", default: \"十二器：提名\")\n#let name = data.at(\"name\", default: \"未知用户\")\n#let title1 = data.at(\"title1\", default: \"暂无\")\n#let evaluate1 = data.at(\"evaluate1\", default: \"暂无推荐语\")\n#let title2 = data.at(\"title2\", default: \"暂无\")\n#let evaluate2 = data.at(\"evaluate2\", default: \"暂无推荐语\")\n#let title3 = data.at(\"title3\", default: \"暂无\")\n#let evaluate3 = data.at(\"evaluate3\", default: \"暂无推荐语\")\n\n#set page(width: 640pt, height: auto, margin: 24pt,\n         fill: gradient.linear(135deg, rgb(\"#e0eafc\"), rgb(\"#cfdef3\")))\n#set text(font: (\"Noto Sans SC\", \"LXGW WenKai\", \"Microsoft YaHei\"),\n          lang: \"zh\", size: 16pt)\n\n#block(fill: white, radius: 16pt, inset: (x: 28pt, y: 24pt))[\n  #text(size: 24pt, weight: \"bold\", fill: rgb(\"#3a7bd5\"))[#header]\n  #v(14pt)\n  #line(length: 100%, stroke: 1pt + rgb(\"#b5c6e0\").transparentize(40%))\n  #v(10pt)\n  #text(weight: \"bold\", fill: rgb(\"#4a6fa5\"))[昵称: ]\n  #text(weight: \"bold\")[#name]\n  #v(8pt)\n  #text(weight: \"bold\", fill: rgb(\"#4a6fa5\"))[提名一: ]\n  #text(weight: \"bold\")[#title1]\n  #v(4pt)\n  #text(fill: rgb(\"#444444\"))[推荐语: #evaluate1]\n  #v(8pt)\n  #text(weight: \"bold\", fill: rgb(\"#4a6fa5\"))[提名二: ]\n  #text(weight: \"bold\")[#title2]\n  #v(4pt)\n  #text(fill: rgb(\"#444444\"))[推荐语: #evaluate2]\n  #v(8pt)\n  #text(weight: \"bold\", fill: rgb(\"#4a6fa5\"))[提名三: ]\n  #text(weight: \"bold\")[#title3]\n  #v(4pt)\n  #text(fill: rgb(\"#444444\"))[推荐语: #evaluate3]\n]\n",
    "render_quality": "high"
  }
}
```

### 简化的报告模板（Typst）

```json
{
  "report": {
    "name": "数据报告模板",
    "description": "用于展示数据统计的简洁模板",
    "typ_content": "#let data = json.decode(sys.inputs.at(\"data\", default: \"{}\"))\n#let title = data.at(\"title\", default: \"数据报告\")\n#let total_users = data.at(\"total_users\", default: \"0\")\n#let active_users = data.at(\"active_users\", default: \"0\")\n#let new_users = data.at(\"new_users\", default: \"0\")\n#let timestamp = data.at(\"timestamp\", default: \"刚刚\")\n\n#set page(width: 700pt, height: auto, margin: 24pt,\n         fill: gradient.linear(135deg, rgb(\"#667eea\"), rgb(\"#764ba2\")))\n#set text(font: (\"Noto Sans SC\", \"Microsoft YaHei\"), lang: \"zh\", size: 14pt)\n\n#block(fill: white, radius: 16pt, inset: (x: 32pt, y: 28pt))[\n  #align(center)[\n    #text(size: 26pt, weight: \"bold\", fill: rgb(\"#2c3e50\"))[#title]\n  ]\n  #v(18pt)\n  #table(\n    columns: (1fr, 1fr),\n    align: (left, right),\n    stroke: 0.5pt + rgb(\"#ecf0f1\"),\n    inset: 12pt,\n    [*总用户数*], [#total_users],\n    [*活跃用户*], [#active_users],\n    [*今日新增*], [#new_users],\n  )\n  #v(16pt)\n  #align(center, text(size: 11pt, fill: rgb(\"#7f8c8d\"))[生成时间: #timestamp])\n]\n",
    "render_quality": "high"
  }
}
```

## 变量使用指南

### 数据注入模型

模板不使用 Jinja2 的 `{{变量}}` 占位符，而是通过 Typst 原生机制接收数据：

1. 插件将请求体的所有键值对聚合为 JSON 字符串
2. 以 `data` 单一入口注入编译参数
3. 模板通过 `sys.inputs.at("data")` 读取并 `json(bytes(...))` 解析

```typst
// 模板开头必须读取数据
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// 读取单个变量（带默认值）
#let name = data.at("name", default: "未知用户")

// 数值转换
#let count = int(data.at("count", default: "0"))

// 数组遍历
#for item in data.at("items", default: ()) [
  - #item
]

// 存在性判断
#if "qr_code" in data [ 显示二维码 ]
```

### 常用变量示例

根据提名模板，常用的变量包括：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `name` | 用户昵称 | `"张三"` |
| `header` | 页面标题 | `"十二器：提名"` |
| `title1` | 第一个提名标题 | `"最佳创意奖"` |
| `evaluate1` | 第一个推荐语 | `"创意十足，令人印象深刻"` |
| `title2` | 第二个提名标题 | `"最佳团队奖"` |
| `evaluate2` | 第二个推荐语 | `"团队协作能力强"` |
| `qr_code` | 二维码图片 hex 字符串 | `"89504e47..."` |
| `qr_text` | 二维码说明文字 | `"扫码参与提名"` |
| `image` | 上传图片 hex 字符串 | `"ffd8ffe0..."` |

## 样式设计技巧

### 1. 渐变背景

```typst
#set page(
  fill: gradient.linear(135deg, rgb("#e0eafc"), rgb("#cfdef3")),
  ...
)
```

### 2. 圆角卡片

```typst
#block(
  fill: white,
  radius: 16pt,
  inset: (x: 28pt, y: 24pt),
)[
  卡片内容
]
```

### 3. 阴影效果（双层卡片模拟）

```typst
#block(fill: rgb("#000").transparentize(80%), radius: 18pt, inset: 0pt)[
  #pad(top: 6pt, left: 6pt)[
    #block(fill: white, radius: 16pt, inset: (x: 28pt, y: 24pt))[...]
  ]
]
```

### 4. 字体设置

```typst
#set text(
  font: ("Noto Sans SC", "LXGW WenKai Lite", "Microsoft YaHei"),
  lang: "zh",
  size: 16pt,
)
```

字体按顺序回退，`typst fonts` 可查看系统可用字体。插件捆绑 `Noto Sans SC`（黑体）与 `LXGW WenKai Lite`（楷体）两个中文字体，通过 `TYPST_FONT_PATHS` 挂载，无系统字体环境也能命中。模板还可在内部以 `// @font-url` 注释声明在线字体 URL，插件下载至本地缓存并即时挂载到字体扫描路径，详见 [Typst模板书写指南](TYPST_TEMPLATE_GUIDE.md) 的字体章节。

### 5. 长文本处理

```typst
// 中文长文本：设置行高与断行
#set text(lang: "zh", overhang: true)
#set par(leading: 1.8em)

// 强制不溢出页面宽度
#set text(hyphenate: true)
```

## API 调用示例

### 使用提名模板

```bash
curl -X POST http://localhost:8080/api/render/image \
  -H "Authorization: Bearer your_token_here" \
  -H "X-Template: nomination" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "name=张三" \
  -F "title1=最佳创意奖" \
  -F "evaluate1=创意十足，令人印象深刻" \
  -F "title2=最佳团队奖" \
  -F "evaluate2=团队协作能力强" \
  -F "title3=最佳技术奖" \
  -F "evaluate3=技术实力雄厚" \
  -F "link=https://example.com/vote"
```

### Python 调用示例

```python
import requests

url = "http://localhost:8080/api/render/image"
headers = {
    "Authorization": "Bearer your_token_here",
    "X-Template": "nomination",
    "X-Target-Type": "group",
    "X-Target-Id": "123456789"
}
data = {
    "name": "张三",
    "title1": "最佳创意奖",
    "evaluate1": "创意十足，令人印象深刻",
    "title2": "最佳团队奖",
    "evaluate2": "团队协作能力强",
    "title3": "最佳技术奖",
    "evaluate3": "技术实力雄厚",
    "link": "https://example.com/vote",
    "qr_text": "扫码参与提名"
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
```

## 常见问题解答

### Q1: 如何在 JSON 中正确转义 Typst 代码？
**A:** 需要对特殊字符进行转义：
- `"` → `\"`
- `\n` → `\\n`（表示换行）
- `\` → `\\`

建议先用本地 `.typ` 文件开发调试，确认无误后再转为 JSON 字符串。

### Q2: 模板渲染失败怎么办？
**A:** 检查以下几点：
1. JSON 格式是否正确
2. Typst 语法是否有误（日志会给出精确的行列号）
3. 模板开头是否有 `sys.inputs.at("data")` 读取语句
4. 是否设置了中文字体与 `lang: "zh"`

### Q3: 如何调试模板？
**A:**
1. 本地安装 Typst CLI，用 `typst compile` 单独编译模板
2. 使用 `typst watch` 实时预览
3. 查看 AstrBot 日志中的 Typst 错误信息（含行列号）
4. 关注日志中使用的渲染路径（Python 绑定 / CLI 后备）

### Q4: 图片质量设置有什么区别？
**A:**
- `low`（72 PPI）: 文件小，适合快速预览
- `medium`（144 PPI）: 平衡质量和文件大小
- `high`（200 PPI）: 高质量，推荐使用
- `ultra`（300 PPI）: 最高质量，用于重要场合

### Q5: 如何优化渲染性能？
**A:**
1. 优先使用 `typst` Python 绑定（内存编译，无进程启动开销）
2. 避免使用过大的图片
3. 合理设置 PPI 档位
4. 保持模板结构简洁

### Q6: 支持哪些 Typst 特性？
**A:** 支持全部 Typst 原生能力：
- 条件、循环、变量、函数
- 表格、网格、定位布局
- 渐变、颜色、图片（含 hex 字符串）
- 数学公式
- 第三方包（通过 Typst 包管理，需注意缓存配置）

---

## 技术支持

如果在配置过程中遇到问题，可以：
1. 查看 AstrBot 插件日志
2. 检查配置 JSON 格式
3. 本地验证 Typst 模板语法
4. 测试数据注入是否正确

希望这个详细教程能帮助您成功配置和使用 HTTP 渲染桥梁插件！
