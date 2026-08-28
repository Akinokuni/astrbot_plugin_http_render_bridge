#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试各种NapCat消息类型
"""

import requests
import json

def test_text_message():
    """测试纯文本消息"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'text',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'text': '这是一条纯文本消息，测试直接发送功能。'
    }
    
    print("🚀 测试纯文本消息...")
    print(f"📋 消息类型: {headers['X-Message-Type']}")
    print(f"📝 内容: {data['text']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ 文本消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_at_message():
    """测试@消息"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'at',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'qq': '123456789',
        'text': '你好！这是一条@消息测试。'
    }
    
    print("\n🚀 测试@消息...")
    print(f"📋 消息类型: {headers['X-Message-Type']}")
    print(f"👤 @用户: {data['qq']}")
    print(f"📝 内容: {data['text']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ @消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_face_message():
    """测试表情消息"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'face',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'face_id': '1'  # QQ表情ID
    }
    
    print("\n🚀 测试表情消息...")
    print(f"📋 消息类型: {headers['X-Message-Type']}")
    print(f"😀 表情ID: {data['face_id']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ 表情消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_share_message():
    """测试链接分享消息"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'share',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'url': 'https://github.com/Akinokuni/astrbot_plugin_http_render_bridge',
        'title': 'AstrBot HTTP渲染桥梁插件',
        'content': '一个强大的HTTP到QQ消息的桥梁插件',
        'image': 'https://github.com/fluidicon.png'
    }
    
    print("\n🚀 测试链接分享消息...")
    print(f"📋 消息类型: {headers['X-Message-Type']}")
    print(f"🔗 链接: {data['url']}")
    print(f"📝 标题: {data['title']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ 链接分享消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_mixed_message():
    """测试混合消息"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Message-Type': 'mixed',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'text': '这是一条混合消息，包含文本和@用户',
        'at': '123456789'
    }
    
    print("\n🚀 测试混合消息...")
    print(f"📋 消息类型: {headers['X-Message-Type']}")
    print(f"📝 文本: {data['text']}")
    print(f"👤 @用户: {data['at']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ 混合消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_template_message():
    """测试传统HTML模板消息（无X-Message-Type头）"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    headers = {
        'X-Html-Template': 'notification',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    data = {
        'title': '兼容性测试',
        'content': '测试在新版本中HTML模板功能是否正常工作',
        'timestamp': '2024-10-30 20:00:00'
    }
    
    print("\n🚀 测试HTML模板消息（兼容性）...")
    print(f"📋 模板: {headers['X-Html-Template']}")
    print(f"📝 标题: {data['title']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ HTML模板消息发送成功！")
            else:
                print(f"❌ 发送失败: {result.get('message')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🎯 开始测试各种NapCat消息类型...")
    print("="*60)
    
    # 测试各种消息类型
    test_text_message()
    test_at_message()
    test_face_message()
    test_share_message()
    test_mixed_message()
    
    # 测试兼容性
    test_template_message()
    
    print("\n" + "="*60)
    print("📝 支持的消息类型:")
    print("1. text - 纯文本消息")
    print("2. image - 图片消息")
    print("3. voice - 语音消息")
    print("4. video - 视频消息")
    print("5. at - @用户消息")
    print("6. reply - 回复消息")
    print("7. forward - 转发消息")
    print("8. face - 表情消息")
    print("9. poke - 戳一戳")
    print("10. shake - 窗口抖动")
    print("11. music - 音乐分享")
    print("12. share - 链接分享")
    print("13. location - 位置分享")
    print("14. mixed - 混合消息")
    print("15. template - HTML模板渲染（默认）")
    print("\n💡 使用方法:")
    print("- 添加 X-Message-Type 头指定消息类型")
    print("- 不添加则默认使用HTML模板渲染")
    print("- 保持向后兼容性")