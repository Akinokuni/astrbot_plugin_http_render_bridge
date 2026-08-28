#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试本地渲染功能
"""

import requests
import json

def test_local_render():
    """测试本地渲染API"""
    
    # API配置
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
    
    # 请求头
    headers = {
        'X-Html-Template': 'notification',
        'X-Target-Type': 'group',
        'X-Target-Id': '123456789',
        'Content-Type': 'multipart/form-data'
    }
    
    print("🚀 开始测试本地渲染功能...")
    print(f"📡 API地址: {base_url}{api_path}")
    print(f"📋 模板: {headers['X-Html-Template']}")
    print(f"🎯 目标: {headers['X-Target-Type']}:{headers['X-Target-Id']}")
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
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ 本地渲染测试成功！")
                print(f"🎨 使用的模板: {result.get('template_used')}")
                print(f"📤 发送目标: {result.get('target')}")
            else:
                print(f"❌ 渲染失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保AstrBot服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_health_check():
    """测试健康检查端点"""
    
    base_url = "http://localhost:11451"
    health_path = "/health"
    
    print("\n🔍 测试健康检查端点...")
    
    try:
        response = requests.get(f"{base_url}{health_path}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查通过")
            print(f"📊 插件状态: {result.get('status')}")
            print(f"🔢 模板数量: {result.get('templates_count')}")
            print("📋 可用模板:")
            for template in result.get('available_templates', []):
                print(f"  - {template['name']}: {template['description']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保AstrBot服务正在运行")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

if __name__ == "__main__":
    # 先测试健康检查
    test_health_check()
    
    # 再测试本地渲染
    test_local_render()
    
    print("\n" + "="*50)
    print("📝 测试说明:")
    print("1. 插件现在强制使用本地渲染")
    print("2. 不再尝试网络渲染服务")
    print("3. HTML模板会被转换为Markdown进行本地渲染")
    print("4. 渲染的图片会保存到本地并发送")