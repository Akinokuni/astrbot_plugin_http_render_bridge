# Typst 模板书写指南

本指南将帮助你为 AstrBot HTTP 渲染桥梁插件创建美观、功能完整的 Typst 模板。

## 目录

- [Typst 简介](#typst-简介)
- [模板基础结构](#模板基础结构)
- [数据注入机制](#数据注入机制)
- [变量读取](#变量读取)
- [条件与循环](#条件与循环)
- [页面与字体设置](#页面与字体设置)
- [颜色、渐变与阴影](#颜色渐变与阴影)
- [表格](#表格)
- [图片支持](#图片支持)
- [二维码支持](#二维码支持)
- [最佳实践](#最佳实践)
- [示例模板](#示例模板)
- [常见问题](#常见问题)

## Typst 简介

Typst 是一款现代化的排版系统，具有以下特点：

- **轻量标记语法** - 类似 Markdown，学习成本低
- **编程式排版** - 内置脚本语言，支持变量、函数、条件、循环
- **编译速度极快** - 毫秒级编译，远快于浏览器渲染
- **原生输出 PNG** - 无需浏览器或 Puppeteer，直接编译为 PNG 图片
- **精确排版** - 排版质量对标 LaTeX，支持中英文混排

插件使用 Typst 将模板编译为 PNG 图片后发送到 QQ。渲染路径：

1. **主路径** - 官方 `typst` Python 绑定（`pip install typst`），内存编译，无磁盘 IO
2. **后备路径** - 系统安装的 `typst` CLI（`typst compile --format png ...`），绑定不可用时自动回退

## 模板基础结构

一个最简 Typst 模板：

```typst
// 1. 读取注入数据（必须位于模板开头）
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// 2. 提取变量（带默认值）
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "这是一条通知消息")

// 3. 页面设置
#set page(width: 600pt, height: auto, margin: 24pt)

// 4. 模板内容
#text(size: 22pt, weight: "bold")[#title]
#v(12pt)
#content
```

### 重要注意事项

1. **数据读取必须在开头** - `sys.inputs.at("data")` 应在模板最顶部调用
2. **始终提供默认值** - 使用 `default:` 参数避免变量缺失时报错
3. **自包含** - 模板应完全独立，外部资源仅支持 URL
4. **中文字体** - 必须设置 `lang: "zh"` 以保证中文正确换行

## 数据注入机制

### JSON 单入口注入

插件将请求体中的所有键值对聚合为一个 JSON 对象，序列化后通过编译参数 `data` 单一入口注入：

```
请求体 form-data:
  title=系统通知
  content=服务器维护
  items=["a", "b"]        (JSON 数组也支持)

注入的 sys.inputs:
  data='{"title": "系统通知", "content": "服务器维护", "items": ["a", "b"]}'
```

### 读取入口数据

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
```

`data` 是一个 Typst 字典（dictionary），可用 `.at(key, default: ...)` 访问任意字段。

## 变量读取

### 基本读取

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// 基本变量
#let title = data.at("title", default: "默认标题")

// 数值类型转换
#let count = int(data.at("count", default: "0"))

// 浮点数
#let rate = float(data.at("rate", default: "0.0"))

// 在文本中使用
标题是：#title，计数是：#count。
```

### 嵌套数据

JSON 支持嵌套结构，可通过 `.at()` 链式访问：

```typst
// 假设注入的 data 为 {"user": {"name": "张三", "level": 5}}
#let user = data.at("user", default: ())
#let name = user.at("name", default: "未知用户")
```

### 数组读取

```typst
// 假设注入的 data 为 {"items": ["告警1", "告警2"]}
#let items = data.at("items", default: ())
#for item in items [
  - #item
]
```

## 条件与循环

Typst 使用原生脚本语法实现逻辑控制，无需额外模板引擎。

### 条件语句

```typst
#let status = data.at("status", default: "info")

#if status == "success" [
  #set text(fill: green)
  操作成功
] else if status == "error" [
  #set text(fill: red)
  操作失败
] else [
  #set text(fill: gray)
  处理中...
]
```

### 循环语句

```typst
#let items = data.at("items", default: ())

// 遍历列表
#for item in items [
  - #item
]

// 带索引的循环（enumerate）
#for (i, item) in items.enumerate() [
  #i + 1. #item
]
```

### 判断字段是否存在

```typst
// "image" 字段存在时才显示图片
#if "image" in data [
  #image(hex-to-bytes(data.at("image")), width: 80%)
]
```

## 页面与字体设置

### 页面尺寸

```typst
// 固定宽度，高度自适应（适合聊天卡片）
#set page(width: 600pt, height: auto, margin: 24pt)

// 完整控制
#set page(
  width: 700pt,          // 页面宽度
  height: auto,          // 高度自适应内容
  margin: 20pt,          // 页边距
  fill: white,           // 页面背景色
)
```

> **像素换算**：输出 PNG 的像素宽度 = 页面宽度(pt) / 72 × PPI。
> 例如 600pt 宽、144 PPI 输出 1200px 宽的图片。

### 中文字体

```typst
// 设置默认字体（含中文回退链）
#set text(
  font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"),
  lang: "zh",            // 中文断行必需
  region: "cn",          // 区域变体（可选）
  size: 14pt,            // 默认字号
)
```

字体按列表顺序回退：列表中的第一个可用字体会被使用。

**捆绑字体**：插件在 `fonts/` 目录下捆绑了轻量中文字体，随插件分发，即使服务器没有安装任何中文字体也能正常渲染中文：

| 字体文件 | Typst 字体族名 | 风格 | 许可证 |
|----------|---------------|------|--------|
| `NotoSansSC-Regular.ttf` | Noto Sans SC | 现代黑体 | SIL Open Font License |
| `LXGWWenKaiLite-Regular.ttf` | LXGW WenKai Lite | 手写楷体 | SIL Open Font License |

捆绑字体目录通过 `TYPST_FONT_PATHS` 环境变量挂载（typst CLI 自动读取），同时官方 Python 绑定在编译时通过 `font_paths` 参数显式传入同一目录，两条渲染路径均无需系统字体即可命中捆绑字体。

**在线字体扩展**：模板可在内部以 `// @font-url` 注释声明在线字体 URL（每行一个），插件渲染时提取声明并异步下载至本地 `font_cache/` 缓存目录，即时挂载到字体扫描路径，Typst 按字体族名匹配使用。同一 URL 的字体只下载一次，后续渲染直接命中缓存离线编译。HTTP 请求不携带任何字体参数：

```typst
// @font-url https://example.com/fonts/ZCOOLQingKeHuangYou-Regular.ttf
#set text(font: ("ZCOOL QingKe HuangYou", "Noto Sans SC"), lang: "zh", size: 14pt)
```

支持 TTF、OTF、TTC、WOFF、WOFF2 格式。

常用中文字体：

| 字体 | 风格 | 平台 |
|------|------|------|
| Noto Sans SC | 现代黑体 | 插件捆绑（fonts/） |
| LXGW WenKai Lite | 手写楷体 | 插件捆绑（fonts/） |
| Noto Sans CJK SC | 思源黑体 | Linux 需安装 `fonts-noto-cjk` |
| Microsoft YaHei | 微软雅黑 | Windows 自带 |
| PingFang SC | 苹方 | macOS 自带 |
| SimHei | 黑体 | Windows 自带 |

> 使用 `typst fonts` 命令可查看系统可用字体。

### 段落样式

```typst
// 标题
#text(size: 24pt, weight: "bold", fill: rgb("#333333"))[#title]

// 正文（1.6 倍行高）
#set par(leading: 1.6em)
#content

// 居中
#align(center, [文本])

// 水平分隔线
#line(length: 100%, stroke: 0.5pt + rgb("#eeeeee"))
```

## 颜色、渐变与阴影

### 颜色

```typst
// RGB / RGBA
#text(fill: rgb("#6366f1"))[...]
#text(fill: rgb(99, 102, 241))[...]
#text(fill: rgb("#000000").lighten(50%))[...]

// 内置颜色
#text(fill: teal)[...]
```

### 渐变背景

```typst
// 线性渐变页面背景
#set page(
  fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg),
  ...
)

// 径向渐变
gradient.radial(rgb("#00b894"), rgb("#00a085"))

```

### 圆角卡片与阴影

Typst 没有 CSS 的 `box-shadow`，可通过"双层卡片"模拟阴影：

```typst
// 阴影层（偏移的浅色卡片）
#block(
  fill: rgb("#000000").transparentize(80%),
  radius: 16pt,
  inset: 0pt,
)[
  #pad(top: 4pt, left: 4pt)[
    // 主体卡片
    #block(
      fill: white,
      radius: 15pt,
      inset: (x: 24pt, y: 20pt),
    )[
      #text(size: 22pt, weight: "bold")[#title]
    ]
  ]
]
```

简化写法（无阴影的圆角卡片）：

```typst
#block(
  fill: white,
  radius: 15pt,
  inset: (x: 24pt, y: 20pt),
)[
  卡片内容
]
```

## 表格

Typst 原生支持表格，非常适合数据报告类模板：

```typst
#table(
  columns: (1fr, 1fr),          // 列宽比例
  align: (left, right),          // 每列对齐方式
  stroke: 0.5pt + rgb("#e5e7eb"), // 边框
  inset: 10pt,                   // 单元格内边距
  fill: (_, row) => if calc.odd(row) { rgb("#f8f9fa") },  // 斑马纹
  [*指标*], [*数值*],
  [总用户数], [#total_users],
  [活跃用户], [#active_users],
  [今日新增], [#new_users],
)
```

更多示例：

```typst
// 无边框的数据行
#table(
  columns: (auto, 1fr),
  stroke: none,
  [名称:], [#name],
  [状态:], [#status],
)

// 带表头的完整表格
#table(
  columns: 3,
  align: (center, center, center),
  table.header(
    [*列1*], [*列2*], [*列3*],
  ),
  [a1], [a2], [a3],
  [b1], [b2], [b3],
)
```

## 图片支持

插件将上传的图片转换为 **hex 字符串** 注入 `data` JSON，模板端通过 `hex-to-bytes` 辅助函数解码为图片字节：

```typst
// 模板开头定义 hex 解码函数（每个模板均需包含）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))
```

### 注入的图片字段

| 字段                                          | 说明            |
| ------------------------------------------- | ------------- |
| `image`                                     | 单张图片的 hex 字符串 |
| `image_filename`                            | 图片原始文件名       |
| `image_size`                                | 图片文件大小（字节）    |
| `image0` / `image1` / ...                   | 多张图片的 hex 字符串 |
| `image0_filename` / `image1_filename` / ... | 对应文件名         |

### 显示单张图片

```typst
#if "image" in data [
  #align(center, image(hex-to-bytes(data.at("image")), width: 80%))
  #if "image_filename" in data [
    #align(center, text(size: 10pt, fill: gray)[#data.at("image_filename")])
  ]
]
```

### 显示多张图片（网格）

```typst
#let extras = (
  (data.at("image0", default: none), data.at("image0_filename", default: none)),
  (data.at("image1", default: none), data.at("image1_filename", default: none)),
  (data.at("image2", default: none), data.at("image2_filename", default: none)),
  (data.at("image3", default: none), data.at("image3_filename", default: none)),
).filter(p => p.at(0) != none)

#if extras.len() > 0 [
  #grid(
    columns: 2,
    gutter: 12pt,
    ..extras.map(p => (
      align(center, image(hex-to-bytes(p.at(0)), width: 100%))
    )),
  )
]
```

### 图片样式

```typst
// 指定宽高
image(hex-to-bytes(data.at("image")), width: 200pt, height: 150pt, fit: "cover")

// 圆角（放入圆形遮罩）
#box(width: 80pt, height: 80pt, radius: 50%, clip: true,
     image(hex-to-bytes(data.at("image")), width: 100%, height: 100%, fit: "cover"))
```

### 使用网络图片

Typst 的 `image()` 直接支持 URL：

```typst
#image("https://example.com/image.jpg", width: 60%)
```

## 二维码支持

传入 `link` 参数后，插件自动生成二维码 PNG，并将其 hex 字符串注入 `data` JSON：

| 字段        | 说明             |
| --------- | -------------- |
| `qr_code` | 二维码图片的 hex 字符串 |
| `qr_text` | 二维码说明文字（可选）    |
| `link`    | 触发二维码生成的原始链接   |

### 右上角显示二维码

```typst
#if "qr_code" in data [
  #place(
    top + right,
    dx: 24pt,
    dy: 24pt,
    block(
      fill: white,
      radius: 12pt,
      inset: 10pt,
      stroke: 0.5pt + rgb("#e5e7eb"),
    )[
      #image(hex-to-bytes(data.at("qr_code")), width: 120pt, height: 120pt)
      #if "qr_text" in data [
        #align(center, text(size: 10pt, fill: gray)[#data.at("qr_text")])
      ]
    ],
  )
]
```

## 最佳实践

### 1. 模板骨架

推荐每个模板使用统一骨架，把数据读取与样式定义放在顶部：

```typst
// ===== 数据区（必选）=====
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// ===== 变量区（带默认值）=====
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "暂无内容")

// ===== 样式区 =====
#let theme = rgb("#6366f1")
#set page(width: 600pt, height: auto, margin: 0pt,
         fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Microsoft YaHei"), lang: "zh", size: 14pt)

// ===== 内容区 =====
...模板内容...
```

### 2. 数据健壮性

```typst
// 始终提供默认值
#let title = data.at("title", default: "未知标题")

// 数值安全转换
#let count = {
  let v = data.at("count", default: "0")
  if type(v) == int { v } else { int(v) }
}

// 判断存在性
#if "image" in data [ ... ]
```

### 3. 性能优化

- 避免过度嵌套的 block 布局
- 图片使用 `width:` 限制尺寸，避免超出版面
- 大数据列表控制在 100 项以内

### 4. 中文排版建议

```typst
#set text(lang: "zh", size: 14pt)
#set par(leading: 1.8em)   // 中文行高建议 1.6~1.8
// 长文本开启断词，避免溢出
#set text(overhang: true)
```

## 示例模板

### 现代通知模板

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "这是一条通知消息")
#let timestamp = data.at("timestamp", default: "刚刚")

#set page(width: 680pt, height: auto, margin: 24pt,
         fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", size: 14pt)

#block(fill: rgb("#000").transparentize(80%), radius: 18pt, inset: 0pt)[
  #pad(top: 6pt, left: 6pt)[
    #block(fill: white, radius: 16pt, inset: (x: 28pt, y: 24pt))[
      #text(size: 24pt, weight: "bold", fill: rgb("#1f2937"))[#title]
      #v(14pt)
      #set par(leading: 1.8em)
      #text(fill: rgb("#374151"))[#content]
      #v(18pt)
      #line(length: 100%, stroke: 0.5pt + rgb("#e5e7eb"))
      #v(10pt)
      #align(center, text(size: 11pt, fill: rgb("#9ca3af"))[#timestamp])
    ]
  ]
]
```

### 数据报告模板

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "数据报告")
#let total_users = data.at("total_users", default: "0")
#let active_users = data.at("active_users", default: "0")
#let new_users = data.at("new_users", default: "0")
#let timestamp = data.at("timestamp", default: "刚刚")

#set page(width: 700pt, height: auto, margin: 24pt,
         fill: gradient.linear(rgb("#74b9ff"), rgb("#0984e3"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"), lang: "zh", size: 14pt)

#block(fill: white, radius: 16pt, inset: (x: 32pt, y: 28pt))[
  #align(center)[
    #text(size: 26pt, weight: "bold", fill: rgb("#2c3e50"))[#title]
    #v(8pt)
    #line(length: 60pt, stroke: 2pt + rgb("#3498db"))
  ]
  #v(20pt)
  #table(
    columns: (1fr, 1fr),
    align: (left, right),
    stroke: 0.5pt + rgb("#ecf0f1"),
    inset: 12pt,
    [*总用户数*], [#total_users],
    [*活跃用户*], [#active_users],
    [*今日新增*], [#new_users],
  )
  #v(16pt)
  #align(center, text(size: 11pt, fill: rgb("#7f8c8d"))[生成时间: #timestamp])
]
```

### 提名展示模板（带二维码）

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let header = data.at("header", default: "提名")
#let name = data.at("name", default: "未知用户")
#let title1 = data.at("title1", default: "暂无")
#let evaluate1 = data.at("evaluate1", default: "暂无推荐语")

#set page(width: 640pt, height: auto, margin: 24pt,
         fill: gradient.linear(rgb("#e0eafc"), rgb("#cfdef3"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", "SimHei"),
          lang: "zh", size: 16pt)

// 右上角二维码
#if "qr_code" in data [
  #place(top + right, dx: 20pt, dy: 20pt,
    block(fill: white, radius: 12pt, inset: 8pt)[
      #image(hex-to-bytes(data.at("qr_code")), width: 110pt, height: 110pt)
      #align(center, text(size: 9pt, fill: gray)[
        #data.at("qr_text", default: "扫码参与")
      ])
    ]
  )
]

#block(fill: white, radius: 16pt, inset: (x: 28pt, y: 24pt))[
  #text(size: 24pt, weight: "bold", fill: rgb("#3a7bd5"))[#header]
  #v(16pt)
  #line(length: 100%, stroke: 1pt + rgb("#b5c6e0").transparentize(40%))
  #v(12pt)
  #text(weight: "bold", fill: rgb("#4a6fa5"))[昵称: ]
  #name
  #v(10pt)
  #text(weight: "bold", fill: rgb("#4a6fa5"))[提名: ]
  #text(weight: "bold")[#title1]
  #v(4pt)
  #text(fill: rgb("#444444"))[推荐语: #evaluate1]
]
```

## 常见问题

### Q: 模板报错 `unknown variable: data`？

A: 确保模板第一行是：

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
```

`sys.inputs.at("data")` 必须在任何读取操作之前执行。

### Q: 中文字符渲染异常或换行错误？

A: 检查 `#set text(...)` 是否包含：

1. 一个已安装的中文字体（`typst fonts` 查看可用字体）
2. `lang: "zh"` 参数

### Q: 图片为什么不显示？

A: 检查：

1. 模板是否定义了 `hex-to-bytes` 辅助函数
2. 字段名是否正确（`image` / `image0` / `qr_code`）
3. 是否使用 `"image" in data` 判断存在性
4. hex 字符串是否完整

### Q: 输出图片的尺寸如何控制？

A: 输出像素 = 页面宽度(pt) / 72 × PPI。

- 版式宽度：模板内 `#set page(width: ...)`
- 像素密度：插件配置的 PPI / 质量档位（72/144/200/300）

### Q: 如何调试模板？

A:

1. 本地安装 Typst CLI 后使用 `typst compile` 直接编译
2. 使用 `typst watch` 实时预览
3. 检查 AstrBot 日志中的 Typst 错误信息（含精确行列号）

### Q: 模板支持哪些 Typst 功能？

A: 插件将模板作为完整 Typst 文档编译，支持全部 Typst 原生能力：

- 变量、函数、条件、循环
- 表格、网格、布局（`place`/`grid`/`block`）
- 渐变、颜色、图片
- 数学公式、图表类包（如 cetz，需自行处理包缓存）

## 参考资源

- [Typst 官方文档](https://typst.app/docs/)
- [Typst 中文入门](https://typst.app/docs/tutorial/)
- [typst Python 绑定 (PyPI)](https://pypi.org/project/typst/)
- [Typst 命令参考](https://typst.app/docs/reference/)

---

**提示**: 创建模板时，建议先用本地 Typst CLI 编译验证语法和排版效果，再集成到插件中。注意测试中文渲染与图片显示效果。
