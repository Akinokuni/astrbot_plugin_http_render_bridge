# HTTP渲染桥梁插件 - 模板配置详细教程

## 📋 目录
1. [配置概述](#配置概述)
2. [内置模板配置](#内置模板配置)
3. [自定义模板配置](#自定义模板配置)
4. [模板示例详解](#模板示例详解)
5. [变量使用指南](#变量使用指南)
6. [样式设计技巧](#样式设计技巧)
7. [常见问题解答](#常见问题解答)

## 配置概述

HTTP渲染桥梁插件支持两种模板配置方式：
- **内置模板**：预设的通知模板，可直接使用
- **自定义模板**：通过JSON配置添加多个自定义模板

## 内置模板配置

### 通知模板设置

在AstrBot管理面板中，找到"HTTP渲染桥梁"插件配置：

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `启用通知模板` | 是否启用内置通知模板 | `true` | `true` |
| `通知模板渲染宽度` | 生成图片的宽度(像素) | `800` | `800` |
| `通知模板图片质量` | 图片质量等级 | `high` | `high/medium/low` |

### 通知模板HTML内容

可以直接编辑内置模板的HTML内容，支持完整的HTML/CSS和Jinja2模板语法。

## 自定义模板配置

### JSON配置格式

在`自定义模板配置`字段中，输入JSON格式的模板配置：

```json
{
  "nomination": {
    "name": "提名模板",
    "description": "用于展示提名信息的模板",
    "html_content": "<!DOCTYPE html>...",
    "render_width": 900,
    "render_quality": "high"
  },
  "report": {
    "name": "报告模板", 
    "description": "数据报告展示模板",
    "html_content": "<!DOCTYPE html>...",
    "render_width": 1200,
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
| `html_content` | string | 是 | 完整的HTML模板内容 |
| `render_width` | number | 否 | 渲染宽度，默认800 |
| `render_quality` | string | 否 | 图片质量：low/medium/high/ultra |

## 模板示例详解

### 基于 http_forwarder/template.html 的提名模板

以下是一个完整的提名模板配置示例：

```json
{
  "nomination": {
    "name": "十二🥥器提名模板",
    "description": "用于展示提名信息的精美模板",
    "html_content": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <meta charset=\\\"utf-8\\\">\\n    <style>\\n        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');\\n        body {\\n            font-family: \\\"LXGWWenKai-Regular\\\", 'Noto Sans SC', sans-serif;\\n            font-size: 22px;\\n            color: #222;\\n            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);\\n            margin: 0;\\n            min-height: 100vh;\\n            display: flex;\\n            align-items: center;\\n            justify-content: center;\\n        }\\n        .card {\\n            background: #fff;\\n            border-radius: 18px;\\n            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);\\n            padding: 40px 36px 32px 36px;\\n            width: auto;\\n            min-width: 260px;\\n            max-width: 90vw;\\n            display: inline-block;\\n        }\\n        .header {\\n            font-size: 2.2em;\\n            font-weight: bold;\\n            color: #3a7bd5;\\n            margin-bottom: 28px;\\n            text-align: left;\\n            letter-spacing: 2px;\\n            text-shadow: 0 2px 8px #e0eafc;\\n            word-break: break-all;\\n        }\\n        .section {\\n            margin-bottom: 22px;\\n            padding: 18px 0 0 0;\\n            border-radius: 10px;\\n            transition: background 0.3s;\\n            word-break: break-all;\\n        }\\n        .section:hover {\\n            background: #f4f8fb;\\n        }\\n        .label {\\n            font-weight: bold;\\n            color: #4a6fa5;\\n            font-size: 1.05em;\\n            letter-spacing: 1px;\\n        }\\n        .value {\\n            margin-left: 10px;\\n            color: #222;\\n            word-break: break-all;\\n        }\\n        .separator {\\n            border-top: 1.5px dashed #b5c6e0;\\n            margin: 18px 0 0 0;\\n        }\\n        .qr-container {\\n            position: fixed;\\n            right: 24px;\\n            top: 24px;\\n            z-index: 999;\\n            background: #fff;\\n            border-radius: 12px;\\n            box-shadow: 0 4px 16px rgba(31,38,135,0.10);\\n            padding: 10px;\\n        }\\n        .qr-image {\\n            display: block;\\n            width: 120px;\\n            height: 120px;\\n        }\\n        .qr-text {\\n            font-size: 12px;\\n            color: #888;\\n            text-align: center;\\n            margin-top: 4px;\\n        }\\n        @media (max-width: 600px) {\\n            .card {\\n                padding: 18px 6vw 18px 6vw;\\n                min-width: unset;\\n                max-width: 98vw;\\n            }\\n            .header {\\n                font-size: 1.3em;\\n            }\\n        }\\n    </style>\\n</head>\\n<body>\\n    <div class=\\\"card\\\">\\n        <div class=\\\"header\\\">{{header | default('十二🥥器：提名')}}</div>\\n        <div class=\\\"section\\\">\\n            <span class=\\\"label\\\">昵称:</span> <span class=\\\"value\\\"><strong>{{ name | default('未知用户') }}</strong></span>\\n        </div>\\n        <div class=\\\"separator\\\"></div>\\n        <div class=\\\"section\\\">\\n            <span class=\\\"label\\\">提名一:</span> <span class=\\\"value\\\"><strong>{{ title1 | default('暂无') }}</strong></span><br>\\n            <span class=\\\"label\\\">推荐语:</span> <span class=\\\"value\\\">{{ evaluate1 | default('暂无推荐语') }}</span>\\n        </div>\\n        <div class=\\\"separator\\\"></div>\\n        <div class=\\\"section\\\">\\n            <span class=\\\"label\\\">提名二:</span> <span class=\\\"value\\\"><strong>{{ title2 | default('暂无') }}</strong></span><br>\\n            <span class=\\\"label\\\">推荐语:</span> <span class=\\\"value\\\">{{ evaluate2 | default('暂无推荐语') }}</span>\\n        </div>\\n        <div class=\\\"separator\\\"></div>\\n        <div class=\\\"section\\\">\\n            <span class=\\\"label\\\">提名三:</span> <span class=\\\"value\\\"><strong>{{ title3 | default('暂无') }}</strong></span><br>\\n            <span class=\\\"label\\\">推荐语:</span> <span class=\\\"value\\\">{{ evaluate3 | default('暂无推荐语') }}</span>\\n        </div>\\n    </div>\\n    {% if qr_code_base64 %}\\n    <div class=\\\"qr-container\\\">\\n        <img src=\\\"data:image/png;base64,{{ qr_code_base64 }}\\\"\\n             alt=\\\"二维码\\\"\\n             class=\\\"qr-image\\\">\\n        <div class=\\\"qr-text\\\">{{ qr_text | default('扫码参与提名') }}</div>\\n    </div>\\n    {% endif %}\\n</body>\\n</html>",
    "render_width": 900,
    "render_quality": "high"
  }
}
```

### 简化的报告模板

```json
{
  "report": {
    "name": "数据报告模板",
    "description": "用于展示数据统计的简洁模板",
    "html_content": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <meta charset=\\\"utf-8\\\">\\n    <style>\\n        body {\\n            font-family: 'Microsoft YaHei', sans-serif;\\n            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\\n            margin: 0;\\n            padding: 20px;\\n            min-height: 100vh;\\n            display: flex;\\n            align-items: center;\\n            justify-content: center;\\n        }\\n        .report-card {\\n            background: white;\\n            border-radius: 20px;\\n            padding: 40px;\\n            box-shadow: 0 15px 35px rgba(0,0,0,0.1);\\n            max-width: 800px;\\n            width: 100%;\\n        }\\n        .report-title {\\n            font-size: 28px;\\n            font-weight: bold;\\n            color: #2c3e50;\\n            text-align: center;\\n            margin-bottom: 30px;\\n            border-bottom: 3px solid #3498db;\\n            padding-bottom: 15px;\\n        }\\n        .data-row {\\n            display: flex;\\n            justify-content: space-between;\\n            align-items: center;\\n            padding: 15px 0;\\n            border-bottom: 1px solid #ecf0f1;\\n        }\\n        .data-label {\\n            font-size: 18px;\\n            color: #34495e;\\n            font-weight: 500;\\n        }\\n        .data-value {\\n            font-size: 24px;\\n            font-weight: bold;\\n            color: #e74c3c;\\n        }\\n        .footer {\\n            text-align: center;\\n            margin-top: 30px;\\n            color: #7f8c8d;\\n            font-size: 14px;\\n        }\\n    </style>\\n</head>\\n<body>\\n    <div class=\\\"report-card\\\">\\n        <div class=\\\"report-title\\\">{{ title | default('数据报告') }}</div>\\n        <div class=\\\"data-row\\\">\\n            <span class=\\\"data-label\\\">总用户数</span>\\n            <span class=\\\"data-value\\\">{{ total_users | default('0') }}</span>\\n        </div>\\n        <div class=\\\"data-row\\\">\\n            <span class=\\\"data-label\\\">活跃用户</span>\\n            <span class=\\\"data-value\\\">{{ active_users | default('0') }}</span>\\n        </div>\\n        <div class=\\\"data-row\\\">\\n            <span class=\\\"data-label\\\">今日新增</span>\\n            <span class=\\\"data-value\\\">{{ new_users | default('0') }}</span>\\n        </div>\\n        <div class=\\\"data-row\\\">\\n            <span class=\\\"data-label\\\">消息总数</span>\\n            <span class=\\\"data-value\\\">{{ total_messages | default('0') }}</span>\\n        </div>\\n        <div class=\\\"footer\\\">\\n            生成时间: {{ timestamp | default('刚刚') }}\\n        </div>\\n    </div>\\n</body>\\n</html>",
    "render_width": 800,
    "render_quality": "high"
  }
}
```

## 变量使用指南

### Jinja2 模板语法

模板使用Jinja2语法，支持以下功能：

#### 1. 变量输出
```html
{{ variable_name }}
{{ variable_name | default('默认值') }}
```

#### 2. 条件判断
```html
{% if condition %}
    <div>显示内容</div>
{% else %}
    <div>其他内容</div>
{% endif %}
```

#### 3. 循环遍历
```html
{% for item in items %}
    <div>{{ item }}</div>
{% endfor %}
```

#### 4. 过滤器
```html
{{ text | upper }}           <!-- 转大写 -->
{{ text | lower }}           <!-- 转小写 -->
{{ number | round(2) }}      <!-- 保留2位小数 -->
{{ text | length }}          <!-- 获取长度 -->
```

### 常用变量示例

根据提名模板，常用的变量包括：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `name` | 用户昵称 | `"张三"` |
| `header` | 页面标题 | `"十二🥥器：提名"` |
| `title1` | 第一个提名标题 | `"最佳创意奖"` |
| `evaluate1` | 第一个推荐语 | `"创意十足，令人印象深刻"` |
| `title2` | 第二个提名标题 | `"最佳团队奖"` |
| `evaluate2` | 第二个推荐语 | `"团队协作能力强"` |
| `title3` | 第三个提名标题 | `"最佳技术奖"` |
| `evaluate3` | 第三个推荐语 | `"技术实力雄厚"` |
| `qr_code_base64` | 二维码Base64数据 | `"iVBORw0KGgoAAAANSUhEUgAA..."` |
| `qr_text` | 二维码说明文字 | `"扫码参与提名"` |

## 样式设计技巧

### 1. 响应式设计

```css
@media (max-width: 600px) {
    .card {
        padding: 18px 6vw;
        min-width: unset;
        max-width: 98vw;
    }
    .header {
        font-size: 1.3em;
    }
}
```

### 2. 渐变背景

```css
background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
```

### 3. 阴影效果

```css
box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
```

### 4. 字体设置

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
font-family: "LXGWWenKai-Regular", 'Noto Sans SC', sans-serif;
```

### 5. 文字换行处理

```css
word-break: break-all;  /* 强制换行 */
word-wrap: break-word;  /* 智能换行 */
```

## API 调用示例

### 使用提名模板

```bash
curl -X POST http://localhost:8080/api/render/image \\
  -H "Authorization: Bearer your_token_here" \\
  -H "X-Html-Template: nomination" \\
  -H "X-Target-Type: group" \\
  -H "X-Target-Id: 123456789" \\
  -F "name=张三" \\
  -F "title1=最佳创意奖" \\
  -F "evaluate1=创意十足，令人印象深刻" \\
  -F "title2=最佳团队奖" \\
  -F "evaluate2=团队协作能力强" \\
  -F "title3=最佳技术奖" \\
  -F "evaluate3=技术实力雄厚" \\
  -F "qr_code_base64=iVBORw0KGgoAAAANSUhEUgAA..."
```

### Python 调用示例

```python
import requests
import base64

# 读取二维码图片并转换为base64
with open('qr_code.png', 'rb') as f:
    qr_base64 = base64.b64encode(f.read()).decode()

url = "http://localhost:8080/api/render/image"
headers = {
    "Authorization": "Bearer your_token_here",
    "X-Html-Template": "nomination",
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
    "qr_code_base64": qr_base64,
    "qr_text": "扫码参与提名"
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
```

## 常见问题解答

### Q1: 如何在JSON中正确转义HTML？
**A:** 需要对特殊字符进行转义：
- `"` → `\\\"`
- `\\n` → `\\\\n`
- `\\` → `\\\\`

### Q2: 模板渲染失败怎么办？
**A:** 检查以下几点：
1. JSON格式是否正确
2. HTML语法是否有误
3. Jinja2变量语法是否正确
4. 是否有未闭合的标签

### Q3: 如何调试模板？
**A:** 
1. 先用简单的HTML测试
2. 逐步添加样式和变量
3. 查看AstrBot日志中的错误信息
4. 使用在线HTML验证工具

### Q4: 图片质量设置有什么区别？
**A:** 
- `low`: 文件小，质量一般，适合快速预览
- `medium`: 平衡质量和文件大小
- `high`: 高质量，文件较大，推荐使用
- `ultra`: 最高质量，文件最大，用于重要场合

### Q5: 如何优化渲染性能？
**A:**
1. 避免使用过大的图片
2. 减少复杂的CSS动画
3. 合理设置渲染宽度
4. 使用适当的图片质量

### Q6: 支持哪些CSS特性？
**A:** 支持大部分CSS3特性，包括：
- Flexbox布局
- Grid布局
- 渐变背景
- 阴影效果
- 字体导入
- 媒体查询

---

## 📞 技术支持

如果在配置过程中遇到问题，可以：
1. 查看AstrBot插件日志
2. 检查配置JSON格式
3. 验证HTML模板语法
4. 测试Jinja2变量是否正确

希望这个详细教程能帮助您成功配置和使用HTTP渲染桥梁插件！🎯