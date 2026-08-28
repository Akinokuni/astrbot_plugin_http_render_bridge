#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试nomination模板的二维码文案
"""

import requests
import json

def test_nomination_qr_text():
    """测试nomination模板的默认二维码文案"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据 - 包含link但不包含qr_text，应该使用模板默认值
    test_data = {
        'name': '测试用户',
        'title1': '最佳创意奖',
        'evaluate1': '这个项目展现了卓越的创新思维',
        'title2': '团队协作奖', 
        'evaluate2': '在团队合作中表现出色',
        'title3': '技术突破奖',
        'evaluate3': '在技术实现上有重大突破',
        'link': 'https://example.com/nomination'
        # 注意：没有提供qr_text，应该使用模板默认值"扫码参与提名"
    }
    
    headers = {
        'X-Template': 'nomination',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    print("🚀 测试nomination模板的默认二维码文案...")
    print(f"📋 模板: {headers['X-Template']}")
    print(f"🔗 链接: {test_data['link']}")
    print("📝 预期: 二维码下方应显示'扫码参与提名'")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            files={k: (None, v) for k, v in test_data.items()}
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 500:
            result = response.json()
            if result.get('message') == 'Failed to send message to target':
                print("✅ 渲染成功！（发送失败是预期的）")
                print("🎯 二维码应该显示'扫码参与提名'")
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 完整流程成功！")
            print("🎯 二维码应该显示'扫码参与提名'")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_custom_qr_text():
    """测试自定义二维码文案"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据 - 包含自定义qr_text
    test_data = {
        'name': '测试用户',
        'title1': '最佳创意奖',
        'evaluate1': '这个项目展现了卓越的创新思维',
        'title2': '团队协作奖', 
        'evaluate2': '在团队合作中表现出色',
        'title3': '技术突破奖',
        'evaluate3': '在技术实现上有重大突破',
        'link': 'https://example.com/nomination',
        'qr_text': '自定义二维码文案'  # 自定义文案
    }
    
    headers = {
        'X-Template': 'nomination',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    print("\n🚀 测试nomination模板的自定义二维码文案...")
    print(f"📋 模板: {headers['X-Template']}")
    print(f"🔗 链接: {test_data['link']}")
    print(f"📝 自定义文案: {test_data['qr_text']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            files={k: (None, v) for k, v in test_data.items()}
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 500:
            result = response.json()
            if result.get('message') == 'Failed to send message to target':
                print("✅ 渲染成功！（发送失败是预期的）")
                print(f"🎯 二维码应该显示'{test_data['qr_text']}'")
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 完整流程成功！")
            print(f"🎯 二维码应该显示'{test_data['qr_text']}'")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 测试默认文案
    test_nomination_qr_text()
    
    # 测试自定义文案
    test_custom_qr_text()
    
    print("\n" + "="*50)
    print("📝 说明:")
    print("1. 不提供qr_text时，nomination模板应显示'扫码参与提名'")
    print("2. 提供qr_text时，应显示自定义文案")
    print("3. 其他模板（notification、success）默认显示'扫码访问链接'")
    print("4. 修改后的逻辑让每个模板可以有自己的默认二维码文案")