#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
仅测试渲染功能，不发送消息
"""

import requests
import json

def test_render_only():
    """测试渲染功能但不发送消息"""
    
    # 我们需要修改插件，添加一个仅渲染不发送的端点
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据
    test_data = {
        'title': '本地渲染测试',
        'content': '这是一个测试本地渲染功能的消息。现在不再使用网络渲染，而是直接使用AstrBot的本地渲染功能。',
        'timestamp': '2024-10-30 15:30:00',
        'sender': '测试用户',
        'type': 'notification'
    }
    
    # 请求头 - 使用一个无效的目标ID来避免实际发送
    headers = {
        'X-Template': 'notification',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',  # 使用无效ID
        'Content-Type': 'multipart/form-data'
    }
    
    print("🚀 开始测试本地渲染功能...")
    print(f"📡 API地址: {base_url}{api_path}")
    print(f"📋 模板: {headers['X-Template']}")
    print(f"📝 数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print("-" * 50)
    
    try:
        # 发送请求
        response = requests.post(
            f"{base_url}{api_path}",
            headers={k: v for k, v in headers.items() if k != 'Content-Type'},
            files={k: (None, v) for k, v in test_data.items()}
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        # 分析响应
        if response.status_code == 500:
            result = response.json()
            if result.get('message') == 'Failed to send message to target':
                print("✅ 渲染成功！（发送失败是预期的，因为使用了无效目标ID）")
            elif result.get('message') == 'Failed to render template to image':
                print("❌ 渲染失败")
            else:
                print(f"❓ 未知错误: {result.get('message')}")
        elif response.status_code == 200:
            result = response.json()
            print("✅ 完整流程成功！")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保AstrBot服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_render_only()
    
    print("\n" + "="*50)
    print("📝 说明:")
    print("如果看到'渲染成功！（发送失败是预期的）'，说明本地渲染功能正常工作")
    print("发送失败是因为使用了无效的目标ID，这是为了避免在测试中实际发送消息")