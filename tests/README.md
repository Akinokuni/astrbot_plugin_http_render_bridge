# 测试脚本目录

这个目录包含了 AstrBot HTTP 渲染桥梁插件的所有测试脚本。

## 测试脚本列表

### 核心功能测试

| 脚本名称 | 功能描述 | 使用方法 |
|---------|----------|----------|
| `test_api.py` | 基础API接口测试 | `python test_api.py` |
| `test_health.py` | 健康检查测试 | `python test_health.py` |
| `test_local_render.py` | 本地渲染功能测试 | `python test_local_render.py` |
| `test_templates.py` | Typst模板渲染测试 | `python test_templates.py` |
| `test_render_only.py` | 纯渲染测试（不发送） | `python test_render_only.py` |
| `test_with_auth.py` | 认证功能测试 | `python test_with_auth.py` |

### 消息类型测试

| 脚本名称 | 功能描述 | 使用方法 |
|---------|----------|----------|
| `test_message_types.py` | NapCat消息类型测试 | `python test_message_types.py` |

### 图片功能测试

| 脚本名称 | 功能描述 | 使用方法 |
|---------|----------|----------|
| `test_image_upload.py` | 图片上传功能测试 | `python test_image_upload.py` |

### 二维码功能测试

| 脚本名称 | 功能描述 | 使用方法 |
|---------|----------|----------|
| `test_qr_code.py` | 二维码生成测试 | `python test_qr_code.py` |
| `test_nomination_qr.py` | 提名模板二维码测试 | `python test_nomination_qr.py` |

### 模板专项测试

| 脚本名称 | 功能描述 | 使用方法 |
|---------|----------|----------|
| `test_nomination_template.py` | 提名模板专项测试 | `python test_nomination_template.py` |

## 运行测试

### 前置条件

1. **启动AstrBot服务** - 确保AstrBot正在运行
2. **插件已加载** - 确保HTTP渲染桥梁插件已正确加载
3. **服务可访问** - 确保可以访问 `http://localhost:11451`

### 快速测试

```bash
# 进入测试目录
cd tests

# 测试健康检查
python test_health.py

# 测试基础功能
python test_api.py

# 测试消息类型
python test_message_types.py

# 测试图片上传
python test_image_upload.py

# 测试二维码功能
python test_qr_code.py
```

### 纯渲染测试

如果只想测试渲染功能而不发送消息：

```bash
python test_render_only.py
```

## 测试说明

### 测试环境

- **默认服务地址**: `http://localhost:11451`
- **API路径**: `/api/render/image`
- **健康检查**: `/health`

### 认证测试

如果插件配置了认证token，某些测试可能会返回401错误。这是正常现象，说明认证机制工作正常。

### 发送失败说明

大部分测试会显示"发送失败"，这是预期的，因为：
1. 使用了无效的目标ID（避免实际发送消息）
2. QQ机器人可能未连接
3. 测试环境中平台客户端不可用

**重要**: 如果看到"渲染成功"的提示，说明核心功能正常工作。

## 测试配置

### 修改测试参数

可以编辑测试脚本中的以下参数：

```python
# 服务地址
base_url = "http://localhost:11451"
api_path = "/api/render/image"

# 目标配置
headers = {
    'X-Target-Type': 'group',
    'X-Target-Id': '000000000',  # 使用无效ID避免实际发送
}

# 认证配置
auth_token = "your_token_here"  # 如果需要认证
```

### 添加认证

如果插件配置了认证，在测试脚本中添加：

```python
headers['Authorization'] = 'Bearer your_token_here'
```

## 测试结果解读

### 成功标识

- **渲染成功** - 核心功能正常
- **完整流程成功** - 包括发送在内的完整流程
- **健康检查通过** - 服务状态正常

### 预期错误

- **需要认证** - 插件配置了认证token
- **发送失败** - 使用无效目标ID，避免实际发送
- **连接失败** - 服务未启动或地址错误

### 实际错误

- **渲染失败** - 模板或数据问题
- **HTTP请求失败** - 网络或服务问题
- **参数错误** - 请求参数不正确

## 开发新测试

### 测试脚本模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本描述
"""

import requests
import json

def test_function():
    """测试函数描述"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'text',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
        'Content-Type': 'application/json'
    }
    
    data = {
        "template": "default",
        "data": {
            "title": "测试标题",
            "content": "测试内容"
        }
    }
    
    try:
        response = requests.post(f"{base_url}{api_path}", 
                               headers=headers, 
                               json=data)
        
        if response.status_code == 200:
            print(" 测试成功")
            print(f"响应: {response.json()}")
        else:
            print(f" 测试失败: {response.status_code}")
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f" 请求异常: {e}")

if __name__ == "__main__":
    test_function()
```

## 测试检查清单

运行测试前请确认：

- [ ] AstrBot服务已启动
- [ ] HTTP渲染桥梁插件已加载
- [ ] 网络连接正常
- [ ] 端口11451未被占用
- [ ] 如有认证配置，token正确

## 相关文档

- [API参考文档](../docs/API_REFERENCE.md)
- [测试指南](../docs/TESTING_GUIDE.md)
- [Typst模板指南](../docs/TYPST_TEMPLATE_GUIDE.md)