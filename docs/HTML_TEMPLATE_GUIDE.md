# HTML 模板书写指南

本指南将帮助你为 AstrBot HTTP 渲染桥梁插件创建美观、功能完整的 HTML 模板。

## 📋 目录

- [基础结构](#基础结构)
- [Jinja2 模板语法](#jinja2-模板语法)
- [CSS 样式指南](#css-样式指南)
- [二维码支持](#二维码支持)
- [响应式设计](#响应式设计)
- [最佳实践](#最佳实践)
- [示例模板](#示例模板)
- [常见问题](#常见问题)

## 🏗️ 基础结构

### 标准HTML模板结构

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* 内联CSS样式 */
    </style>
</head>
<body>
    <!-- 模板内容 -->
</body>
</html>
```

### 重要注意事项

1. **必须使用完整的HTML文档结构**
2. **CSS必须内联** - 不支持外部CSS文件
3. **字符编码** - 始终使用 `<meta charset="utf-8">`
4. **自包含** - 模板应该是完全独立的

## 🔧 Jinja2 模板语法

### 变量输出

```html
<!-- 基本变量 -->
<div>{{title}}</div>

<!-- 带默认值的变量 -->
<div>{{title | default('默认标题')}}</div>

<!-- 安全输出（防止HTML注入） -->
<div>{{content | e}}</div>
```

### 条件语句

```html
<!-- 简单条件 -->
{% if user_name %}
<div>欢迎，{{user_name}}！</div>
{% endif %}

<!-- 条件分支 -->
{% if status == 'success' %}
<div class="success">操作成功</div>
{% elif status == 'error' %}
<div class="error">操作失败</div>
{% else %}
<div class="info">处理中...</div>
{% endif %}
```

### 循环语句

```html
<!-- 遍历列表 -->
{% for item in items %}
<div class="item">{{item.name}}: {{item.value}}</div>
{% endfor %}

<!-- 带索引的循环 -->
{% for item in items %}
<div class="item-{{loop.index}}">{{item}}</div>
{% endfor %}
```

### 过滤器

```html
<!-- 常用过滤器 -->
<div>{{text | upper}}</div>          <!-- 大写 -->
<div>{{text | lower}}</div>          <!-- 小写 -->
<div>{{text | title}}</div>          <!-- 标题格式 -->
<div>{{number | round(2)}}</div>     <!-- 四舍五入 -->
<div>{{timestamp | default('刚刚')}}</div> <!-- 默认值 -->
```

## 🎨 CSS 样式指南

### 推荐的CSS结构

```css
/* 1. 重置和基础样式 */
body {
    margin: 0;
    padding: 0;
    font-family: 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
}

/* 2. 布局样式 */
.container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}

/* 3. 组件样式 */
.card {
    background: white;
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* 4. 响应式样式 */
@media (max-width: 600px) {
    .card {
        padding: 20px;
        margin: 10px;
    }
}
```

### 颜色和渐变

```css
/* 推荐的颜色方案 */
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.success-theme {
    background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.warning-theme {
    background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
}

.info-theme {
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
}
```

### 阴影和效果

```css
/* 现代阴影效果 */
.card-shadow {
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
}

.hover-effect {
    transition: all 0.3s ease;
}

.hover-effect:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
```

## 📱 二维码支持

### 基本二维码结构

```html
<!-- 二维码容器（条件显示） -->
{% if qr_code_base64 %}
<div class="qr-container">
    <img src="data:image/png;base64,{{ qr_code_base64 }}"
         alt="二维码"
         class="qr-image">
    <div class="qr-text">{{ qr_text | default('扫码访问链接') }}</div>
</div>
{% endif %}
```

### 二维码CSS样式

```css
.qr-container {
    position: fixed;
    right: 24px;
    top: 24px;
    z-index: 999;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(31,38,135,0.10);
    padding: 10px;
}

.qr-image {
    display: block;
    width: 120px;
    height: 120px;
}

.qr-text {
    font-size: 12px;
    color: #888;
    text-align: center;
    margin-top: 4px;
}
```

### 二维码参数

- **`qr_code_base64`** - 自动生成（当传入`link`参数时）
- **`qr_text`** - 二维码下方文字（可选）
- **`link`** - 要生成二维码的链接（插件自动处理）

## 📱 响应式设计

### 移动端适配

```css
/* 基础响应式断点 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .card {
        width: 95%;
        padding: 20px;
    }
    
    .title {
        font-size: 1.5em;
    }
}

@media (max-width: 480px) {
    .card {
        padding: 15px;
    }
    
    .title {
        font-size: 1.2em;
    }
    
    /* 移动端隐藏二维码 */
    .qr-container {
        display: none;
    }
}
```

### 字体大小适配

```css
/* 使用相对单位 */
.title {
    font-size: clamp(1.2rem, 4vw, 2.5rem);
}

.content {
    font-size: clamp(0.9rem, 2.5vw, 1.1rem);
    line-height: 1.6;
}
```

## ✨ 最佳实践

### 1. 性能优化

```css
/* 使用高效的CSS选择器 */
.card { /* 好 */ }
div.card { /* 避免 */ }
.container .card .title { /* 避免过深嵌套 */ }

/* 避免复杂的CSS效果 */
.simple-transition {
    transition: opacity 0.3s ease;
}
```

### 2. 可读性

```html
<!-- 使用语义化的类名 -->
<div class="notification-card">
    <div class="notification-header">
        <h2 class="notification-title">{{title}}</h2>
    </div>
    <div class="notification-body">
        <p class="notification-content">{{content}}</p>
    </div>
    <div class="notification-footer">
        <span class="notification-time">{{timestamp}}</span>
    </div>
</div>
```

### 3. 错误处理

```html
<!-- 始终提供默认值 -->
<div class="title">{{title | default('未知标题')}}</div>
<div class="content">{{content | default('暂无内容')}}</div>

<!-- 处理可能为空的数据 -->
{% if items and items|length > 0 %}
    {% for item in items %}
    <div>{{item}}</div>
    {% endfor %}
{% else %}
    <div class="empty-state">暂无数据</div>
{% endif %}
```

### 4. 字体和编码

```css
/* 推荐的中文字体栈 */
body {
    font-family: 
        "PingFang SC",
        "Hiragino Sans GB", 
        "Microsoft YaHei",
        "WenQuanYi Micro Hei",
        "Helvetica Neue",
        Arial,
        sans-serif;
}

/* 确保文字渲染质量 */
body {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}
```

## 📝 示例模板

### 简单通知模板

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 100%;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }
        .content {
            font-size: 16px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .footer {
            font-size: 12px;
            color: #999;
            text-align: center;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }
        .qr-container {
            position: fixed;
            right: 24px;
            top: 24px;
            z-index: 999;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(31,38,135,0.10);
            padding: 10px;
        }
        .qr-image {
            display: block;
            width: 120px;
            height: 120px;
        }
        .qr-text {
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 4px;
        }
        @media (max-width: 600px) {
            .card {
                padding: 20px;
                margin: 10px;
            }
            .qr-container {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="title">{{title | default('通知')}}</div>
        <div class="content">{{content | default('这是一条通知消息')}}</div>
        <div class="footer">{{timestamp | default('刚刚')}}</div>
    </div>
    {% if qr_code_base64 %}
    <div class="qr-container">
        <img src="data:image/png;base64,{{ qr_code_base64 }}"
             alt="二维码"
             class="qr-image">
        <div class="qr-text">{{ qr_text | default('扫码访问链接') }}</div>
    </div>
    {% endif %}
</body>
</html>
```

### 数据展示模板

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .report-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 100%;
        }
        .report-title {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .data-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        .data-label {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .data-value {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
            border-top: 1px solid #ecf0f1;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="report-card">
        <div class="report-title">{{title | default('数据报告')}}</div>
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">总用户数</div>
                <div class="data-value">{{total_users | default('0')}}</div>
            </div>
            <div class="data-item">
                <div class="data-label">活跃用户</div>
                <div class="data-value">{{active_users | default('0')}}</div>
            </div>
            <div class="data-item">
                <div class="data-label">今日新增</div>
                <div class="data-value">{{new_users | default('0')}}</div>
            </div>
            <div class="data-item">
                <div class="data-label">消息总数</div>
                <div class="data-value">{{total_messages | default('0')}}</div>
            </div>
        </div>
        <div class="footer">
            生成时间: {{timestamp | default('刚刚')}}
        </div>
    </div>
</body>
</html>
```

## ❓ 常见问题

### Q: 为什么我的CSS样式没有生效？

A: 确保：
1. CSS 必须写在 `<style>` 标签内（内联样式）
2. 不能使用外部 CSS 文件
3. 检查 CSS 语法是否正确

### Q: 如何调试模板？

A: 
1. 使用浏览器直接打开 HTML 文件预览
2. 使用插件的测试脚本验证渲染效果
3. 检查 AstrBot 日志中的错误信息

### Q: 模板中的图片如何处理？

A: 
1. 使用 base64 编码的图片：`<img src="data:image/png;base64,...">`
2. 使用网络图片：`<img src="https://...">`
3. 二维码会自动处理，只需传入 `link` 参数

### Q: 如何优化渲染性能？

A:
1. 避免复杂的 CSS 动画和效果
2. 使用简洁的 HTML 结构
3. 避免过多的嵌套元素
4. 使用高效的 CSS 选择器

### Q: 模板支持哪些 Jinja2 功能？

A: 支持大部分 Jinja2 功能：
- 变量输出和过滤器
- 条件语句（if/elif/else）
- 循环语句（for）
- 模板继承（extends/block）
- 宏定义（macro）

## 🚀 进阶技巧

### 1. 使用CSS变量

```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2c3e50;
    --border-radius: 10px;
    --shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.card {
    background: var(--primary-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
}
```

### 2. 创建可复用的组件样式

```css
/* 按钮组件 */
.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-success {
    background: #27ae60;
    color: white;
}

/* 状态指示器 */
.status {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.status-success {
    background: #d4edda;
    color: #155724;
}

.status-error {
    background: #f8d7da;
    color: #721c24;
}
```

### 3. 高级布局技巧

```css
/* Flexbox 布局 */
.flex-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

/* Grid 布局 */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

/* 粘性定位 */
.sticky-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 100;
}
```

---

## 📚 参考资源

- [Jinja2 官方文档](https://jinja.palletsprojects.com/)
- [CSS Grid 指南](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Flexbox 指南](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [响应式设计指南](https://web.dev/responsive-web-design-basics/)

---

**提示**: 创建模板时，建议先在浏览器中测试 HTML 文件，确认样式和布局正确后再集成到插件中。