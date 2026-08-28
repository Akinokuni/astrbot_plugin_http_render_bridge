# 图片上传功能使用指南

本指南介绍如何在 AstrBot HTTP 渲染桥梁插件中使用图片上传功能。

## 功能概述

插件支持通过 HTTP 请求上传图片文件，并将其嵌入到 Typst 模板中进行渲染。图片会自动转换为 hex 字符串注入模板数据，模板通过 `hex-to-bytes` 辅助函数解码为图片字节，无需额外的文件存储。

## 支持的功能

- **多种图片格式**: JPG, JPEG, PNG, GIF, WebP
- **文件大小限制**: 最大 5MB
- **自动转换**: 图片自动转换为 hex 字符串
- **多图片支持**: 一次请求可以上传多张图片
- **模板集成**: 图片可以在任何 Typst 模板中显示（需定义 `hex-to-bytes` 辅助函数）
- **文件信息**: 自动提供文件名和大小信息

## 使用方法

### 基本用法

使用 `multipart/form-data` 格式发送请求，包含图片文件：

```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Template: notification" \
  -H "X-Target-Type: group" \
  -H "X-Target-Id: 123456789" \
  -F "title=图片通知" \
  -F "content=这是一条包含图片的通知" \
  -F "image=@/path/to/your/image.jpg"
```

### Python 示例

```python
import requests

url = "http://localhost:11451/api/render/image"
headers = {
    "X-Template": "notification",
    "X-Target-Type": "group",
    "X-Target-Id": "123456789"
}

# 文本数据
data = {
    "title": "图片通知",
    "content": "这是一条包含图片的通知消息"
}

# 图片文件
with open("image.jpg", "rb") as f:
    files = {"image": ("image.jpg", f, "image/jpeg")}
    response = requests.post(url, headers=headers, data=data, files=files)
```

### 多图片上传

```python
# 上传多张图片
files = {
    "image0": ("photo1.jpg", open("photo1.jpg", "rb"), "image/jpeg"),
    "image1": ("photo2.png", open("photo2.png", "rb"), "image/png"),
    "image2": ("photo3.gif", open("photo3.gif", "rb"), "image/gif")
}

response = requests.post(url, headers=headers, data=data, files=files)
```

## 模板中使用图片

### 基本图片显示

```typst
// 模板开头定义 hex 解码函数（每个模板均需包含）
#let hex-to-bytes(s) = bytes(range(0, calc.floor(s.len() / 2)).map(i => int(s.slice(i * 2, i * 2 + 2), base: 16)))

// 模板开头读取数据
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// 显示单张图片（存在性判断）
#if "image" in data [
  #align(center, image(hex-to-bytes(data.at("image")), width: 80%, fit: "contain"))
  #if "image_filename" in data [
    #align(center, text(size: 10pt, fill: gray)[#data.at("image_filename")])
  ]
]
```

### 多图片网格布局

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))

// 收集 image0 ~ image3
#let images = ()
#for i in range(4) {
  let key = "image" + str(i)
  if key in data {
    images.push((data.at(key), data.at(key + "_filename", default: "")))
  }
}

// 网格显示
#if images.len() > 0 [
  #grid(
    columns: 2,
    gutter: 12pt,
    ..images.map(((uri, name)) => block(
      fill: rgb("#f8f9fa"),
      radius: 10pt,
      inset: 8pt,
      align(center)[
        #image(hex-to-bytes(uri), width: 100%, fit: "contain")
        #v(4pt)
        #text(size: 9pt, fill: gray)[#name]
      ],
    )),
  )
]
```

### 图片样式控制

```typst
// 指定宽高（fit 裁切）
#image(hex-to-bytes(data.at("image")), width: 200pt, height: 150pt, fit: "cover")

// 圆角显示（裁剪遮罩）
#box(
  width: 120pt,
  height: 120pt,
  radius: 12pt,
  clip: true,
  image(hex-to-bytes(data.at("image")), width: 100%, height: 100%, fit: "cover"),
)
```

## 可用的模板变量

当上传图片时，插件会自动将以下字段注入 `data` JSON：

### 单图片字段 (字段名: `image`)
- `image` - 图片的 hex 字符串
- `image_filename` - 原始文件名
- `image_size` - 文件大小（字节）

### 多图片字段 (字段名: `image0`, `image1`, 等)
- `image0` - 第一张图片的 hex 字符串
- `image0_filename` - 第一张图片的文件名
- `image0_size` - 第一张图片的大小
- `image1` - 第二张图片的 hex 字符串
- `image1_filename` - 第二张图片的文件名
- `image1_size` - 第二张图片的大小
- ... 以此类推

## 技术细节

### 文件处理流程

1. **接收文件** - 通过 multipart/form-data 接收
2. **格式验证** - 检查文件扩展名和 MIME 类型
3. **大小检查** - 限制最大 5MB
4. **Hex 转换** - 转换为 hex 字符串
5. **数据注入** - 写入 `data` JSON 对象，随 `sys.inputs` 注入模板

### 支持的 MIME 类型

- `image/jpeg` - JPG, JPEG 文件
- `image/png` - PNG 文件
- `image/gif` - GIF 文件
- `image/webp` - WebP 文件

### 安全限制

- **文件大小**: 最大 5MB
- **文件类型**: 仅支持图片格式
- **扩展名检查**: 基于文件扩展名验证
- **内存处理**: 图片完全在内存中处理，不写入磁盘

## 示例模板

### 通知模板 (notification.typ)

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "通知")
#let content = data.at("content", default: "这是一条通知消息")
#let timestamp = data.at("timestamp", default: "刚刚")

#set page(width: 620pt, height: auto, margin: 24pt,
         fill: gradient.linear(rgb("#667eea"), rgb("#764ba2"), angle: 135deg))
#set text(font: ("Noto Sans SC", "Microsoft YaHei"), lang: "zh", size: 14pt)

#block(fill: white, radius: 15pt, inset: (x: 26pt, y: 22pt))[
  #text(size: 22pt, weight: "bold", fill: rgb("#333333"))[#title]
  #v(10pt)
  #set par(leading: 1.7em)
  #text(fill: rgb("#666666"))[#content]

  // 图片显示
  #if "image" in data [
    #v(14pt)
    #align(center, image(hex-to-bytes(data.at("image")), width: 90%, fit: "contain"))
    #if "image_filename" in data [
      #v(6pt)
      #align(center, text(size: 10pt, fill: gray)[#data.at("image_filename")])
    ]
  ]

  #v(16pt)
  #line(length: 100%, stroke: 0.5pt + rgb("#eeeeee"))
  #v(8pt)
  #align(center, text(size: 10pt, fill: rgb("#999999"))[#timestamp])
]
```

### 图片展示模板 (image_showcase.typ)

专门用于展示多张图片的模板，支持网格布局和单图显示。

```typst
#let data = json(bytes(sys.inputs.at("data", default: "{}")))
#let title = data.at("title", default: "图片展示")

#set page(width: 700pt, height: auto, margin: 24pt, fill: white)
#set text(font: ("Noto Sans SC", "Microsoft YaHei"), lang: "zh", size: 14pt)

#text(size: 20pt, weight: "bold")[#title]
#v(14pt)

// 收集所有 imageN 图片
#let images = ()
#for i in range(10) {
  let key = "image" + str(i)
  if key in data {
    images.push(data.at(key))
  }
}

#if images.len() > 0 [
  #grid(
    columns: 2,
    gutter: 14pt,
    ..images.map(uri => block(
      fill: rgb("#f8f9fa"),
      radius: 12pt,
      inset: 10pt,
      align(center, image(hex-to-bytes(uri), width: 100%, fit: "contain")),
    )),
  )
] else [
  #align(center, text(fill: gray)[暂无图片])
]
```

## 常见问题

### Q: 为什么我的图片没有显示？

A: 检查以下几点：
1. 确保使用 `multipart/form-data` 格式
2. 图片文件大小不超过 5MB
3. 图片格式在支持列表中
4. 模板中使用了 `"image" in data` 存在性判断
5. 模板中使用了 `"image" in data` 存在性判断，且 `hex-to-bytes` 辅助函数已定义

### Q: 如何上传多张图片？

A: 使用不同的字段名，如 `image0`, `image1`, `image2` 等：

```python
files = {
    "image0": ("photo1.jpg", open("photo1.jpg", "rb"), "image/jpeg"),
    "image1": ("photo2.png", open("photo2.png", "rb"), "image/png")
}
```

### Q: 图片质量如何控制？

A: 图片会保持原始质量转换为 hex 字符串。如需压缩，请在上传前处理图片。最终输出图片的整体清晰度由插件配置的 PPI 档位控制（72/144/200/300）。

### Q: 支持动图吗？

A: Typst 编译输出为静态 PNG 图片。GIF 文件可以上传和显示第一帧，但不保留动画效果。

### Q: 如何在模板中设置图片样式？

A: 使用 Typst 的 `image()` 函数参数：

```typst
// 宽度、高度、裁切方式
#image(hex-to-bytes(data.at("image")), width: 80%, height: 200pt, fit: "cover")

// 圆角裁剪
#box(radius: 12pt, clip: true, image(hex-to-bytes(data.at("image")), width: 100%))
```

## 高级用法

### 响应式宽度

```typst
// 相对页面宽度
#image(hex-to-bytes(data.at("image")), width: 80%)

// 固定尺寸
#image(hex-to-bytes(data.at("image")), width: 300pt)
```

### 图片网格布局

```typst
#grid(
  columns: (1fr, 1fr),  // 两列等宽
  gutter: 16pt,
  image(hex-to-bytes(data.at("image0")), width: 100%, fit: "cover"),
  image(hex-to-bytes(data.at("image1")), width: 100%, fit: "cover"),
  image(hex-to-bytes(data.at("image2")), width: 100%, fit: "cover"),
)
```

### 图片与文字混排

```typst
#set align(center)
#image(hex-to-bytes(data.at("image")), width: 40%)
#v(8pt)
#text(size: 10pt, fill: gray)[图片说明文字]
```

---

## 相关文档

- [Typst模板书写指南](TYPST_TEMPLATE_GUIDE.md)
- [模板配置指南](TEMPLATE_CONFIG_GUIDE.md)
- [部署指南](DEPLOYMENT.md)

---

**提示**: 图片上传功能与二维码功能可以同时使用，创建更丰富的视觉内容。
