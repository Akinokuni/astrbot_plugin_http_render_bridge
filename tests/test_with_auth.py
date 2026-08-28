#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
带认证的渲染测试
"""

import requests
import json

def test_with_auth():
    """测试带认证的渲染功能"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据
    test_data = {
        'title': '本地渲染测试',
        'content': '这是一个测试本地渲染功能的消息。现在强制使用本地渲染，避免网络渲染的问题。',
        'timestamp': '2024-10-30 15:30:00',
        'sender': '测试用户',
        'type': 'notification'
    }
    
    # 请求头 - 不包含认证，测试是否跳过认证
    headers = {
        'X-Template': 'notification',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',  # 使用无效ID避免实际发送
    }
    
    print("🚀 开始测试本地渲染功能（无认证）...")
    print(f"📡 API地址: {base_url}{api_path}")
    print(f"📋 模板: {headers['X-Template']}")
    print(f"📝 数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    print("-" * 50)
    
    try:
        # 发送请求
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            files={k: (None, v) for k, v in test_data.items()}
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        # 分析响应
        if response.status_code == 500:
            result = response.json()
            if result.get('message') == 'Failed to send message to target':
                print("✅ 渲染成功！（发送失败是预期的）")
            elif result.get('message') == 'Failed to render template to image':
                print("❌ 渲染失败")
            else:
                print(f"❓ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            result = response.json()
            print("✅ 完整流程成功！")
        elif response.status_code == 401:
            print("🔐 需要认证，插件配置了auth_token")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保AstrBot服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_with_auth()
    
    print("\n" + "="*50)
    print("📝 说明:")
    print("如果返回401，说明插件配置了认证token")
    print("如果看到'渲染成功！'，说明本地渲染功能正常工作")
    print("文件路径问题已经修复，现在会检查文件存在性并使用绝对路径")