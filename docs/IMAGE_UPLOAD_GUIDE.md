# 图片上传功能使用指南

本指南介绍如何在 AstrBot HTTP 渲染桥梁插件中使用图片上传功能。

## 📋 功能概述

插件现在支持通过 HTTP 请求上传图片文件，并将其嵌入到 HTML 模板中进行渲染。图片会自动转换为 base64 格式，无需额外的文件存储。

## 🎯 支持的功能

- ✅ **多种图片格式**: JPG, JPEG, PNG, GIF, WebP, BMP
- ✅ **文件大小限制**: 最大 5MB
- ✅ **自动转换**: 图片自动转换为 base64 数据URI
- ✅ **多图片支持**: 一次请求可以上传多张图片
- ✅ **模板集成**: 图片可以在任何 HTML 模板中显示
- ✅ **文件信息**: 自动提供文件名和大小信息

## 🚀 使用方法

### 基本用法

使用 `multipart/form-data` 格式发送请求，包含图片文件：

```bash
curl -X POST http://localhost:11451/api/render/image \
  -H "X-Html-Template: notification" \
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
    "X-Html-Template": "notification",
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

## 🎨 模板中使用图片

### 基本图片显示

```html
<!-- 显示单张图片 -->
{% if image %}
<div class="image-container">
    <img src="{{ image }}" alt="上传的图片" class="uploaded-image">
    {% if image_filename %}
    <div class="image-caption">{{ image_filename }}</div>
    {% endif %}
</div>
{% endif %}
```

### 多图片网格布局

```html
<!-- 多图片网格 -->
<div class="image-grid">
    {% if image0 %}
    <div class="image-item">
        <img src="{{ image0 }}" alt="图片1">
        <div class="filename">{{ image0_filename }}</div>
    </div>
    {% endif %}
    
    {% if image1 %}
    <div class="image-item">
        <img src="{{ image1 }}" alt="图片2">
        <div class="filename">{{ image1_filename }}</div>
    </div>
    {% endif %}
</div>
```

### 推荐的CSS样式

```css
.image-container {
    margin: 20px 0;
    text-align: center;
}

.uploaded-image {
    max-width: 100%;
    max-height: 300px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.image-caption {
    font-size: 12px;
    color: #888;
    margin-top: 8px;
    font-style: italic;
}

.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.image-item {
    text-align: center;
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
}

.image-item img {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
}
```

## 📝 可用的模板变量

当上传图片时，插件会自动提供以下变量：

### 单图片字段 (字段名: `image`)
- `{{ image }}` - 图片的 base64 数据URI
- `{{ image_filename }}` - 原始文件名
- `{{ image_size }}` - 文件大小（字节）

### 多图片字段 (字段名: `image0`, `image1`, 等)
- `{{ image0 }}` - 第一张图片的 base64 数据URI
- `{{ image0_filename }}` - 第一张图片的文件名
- `{{ image0_size }}` - 第一张图片的大小
- `{{ image1 }}` - 第二张图片的 base64 数据URI
- `{{ image1_filename }}` - 第二张图片的文件名
- `{{ image1_size }}` - 第二张图片的大小
- ... 以此类推

## 🔧 技术细节

### 文件处理流程

1. **接收文件** - 通过 multipart/form-data 接收
2. **格式验证** - 检查文件扩展名和MIME类型
3. **大小检查** - 限制最大 5MB
4. **Base64转换** - 转换为 `data:image/type;base64,xxx` 格式
5. **模板传递** - 作为变量传递给 Jinja2 模板

### 支持的MIME类型

- `image/jpeg` - JPG, JPEG 文件
- `image/png` - PNG 文件
- `image/gif` - GIF 文件
- `image/webp` - WebP 文件
- `image/bmp` - BMP 文件

### 安全限制

- **文件大小**: 最大 5MB
- **文件类型**: 仅支持图片格式
- **扩展名检查**: 基于文件扩展名验证
- **内存处理**: 图片完全在内存中处理，不写入磁盘

## 📋 示例模板

### 通知模板 (notification.html)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 600px;
        }
        .image-container {
            margin: 20px 0;
            text-align: center;
        }
        .uploaded-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>{{title | default('通知')}}</h2>
        <p>{{content | default('这是一条通知消息')}}</p>
        
        {% if image %}
        <div class="image-container">
            <img src="{{ image }}" alt="上传的图片" class="uploaded-image">
            {% if image_filename %}
            <div class="image-caption">{{ image_filename }}</div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="footer">{{timestamp | default('刚刚')}}</div>
    </div>
</body>
</html>
```

### 图片展示模板 (image_showcase.html)

专门用于展示多张图片的模板，支持网格布局和单图显示。

## ❓ 常见问题

### Q: 为什么我的图片没有显示？

A: 检查以下几点：
1. 确保使用 `multipart/form-data` 格式
2. 图片文件大小不超过 5MB
3. 图片格式在支持列表中
4. 模板中正确使用了 `{{ image }}` 变量

### Q: 如何上传多张图片？

A: 使用不同的字段名，如 `image0`, `image1`, `image2` 等：

```python
files = {
    "image0": ("photo1.jpg", open("photo1.jpg", "rb"), "image/jpeg"),
    "image1": ("photo2.png", open("photo2.png", "rb"), "image/png")
}
```

### Q: 图片质量如何控制？

A: 图片会保持原始质量转换为 base64。如需压缩，请在上传前处理图片。

### Q: 支持动图吗？

A: 支持 GIF 格式的动图，会保持动画效果。

### Q: 如何在模板中设置图片样式？

A: 使用 CSS 控制图片显示：

```css
.uploaded-image {
    max-width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 10px;
}
```

## 🚀 高级用法

### 响应式图片

```css
.responsive-image {
    width: 100%;
    height: auto;
    max-width: 600px;
}

@media (max-width: 768px) {
    .responsive-image {
        max-width: 100%;
    }
}
```

### 图片懒加载效果

```css
.image-container {
    opacity: 0;
    animation: fadeIn 0.5s ease-in forwards;
}

@keyframes fadeIn {
    to {
        opacity: 1;
    }
}
```

### 图片网格布局

```css
.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.image-item {
    position: relative;
    overflow: hidden;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.image-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.image-item:hover img {
    transform: scale(1.05);
}
```

---

## 📚 相关文档

- [HTML模板书写指南](HTML_TEMPLATE_GUIDE.md)
- [插件配置指南](TEMPLATE_CONFIG_GUIDE.md)
- [部署指南](DEPLOYMENT.md)

---

**提示**: 图片上传功能与二维码功能可以同时使用，创建更丰富的视觉内容。