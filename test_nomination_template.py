#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试nomination模板的二维码功能
"""

import requests
import json

def test_nomination_with_qr():
    """测试nomination模板，包含二维码数据"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据 - 包含二维码base64数据
    test_data = {
        'name': '测试用户',
        'title1': '最佳创意奖',
        'evaluate1': '这个项目展现了卓越的创新思维和技术实现能力',
        'title2': '团队协作奖', 
        'evaluate2': '在团队合作中表现出色，能够有效协调各方资源',
        'title3': '技术突破奖',
        'evaluate3': '在技术实现上有重大突破，为行业发展做出贡献',
        'qr_code_base64': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',  # 1x1像素的透明PNG
        'qr_text': '扫码参与提名'
    }
    
    headers = {
        'X-Html-Template': 'nomination',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    print("🚀 测试nomination模板（包含二维码）...")
    print(f"📋 模板: {headers['X-Html-Template']}")
    print(f"📝 数据: {json.dumps({k: v if k != 'qr_code_base64' else f'{v[:20]}...' for k, v in test_data.items()}, ensure_ascii=False, indent=2)}")
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
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 完整流程成功！")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_nomination_without_qr():
    """测试nomination模板，不包含二维码数据"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据 - 不包含二维码
    test_data = {
        'name': '测试用户',
        'title1': '最佳创意奖',
        'evaluate1': '这个项目展现了卓越的创新思维',
        'title2': '团队协作奖', 
        'evaluate2': '在团队合作中表现出色',
        'title3': '技术突破奖',
        'evaluate3': '在技术实现上有重大突破'
        # 注意：没有qr_code_base64参数
    }
    
    headers = {
        'X-Html-Template': 'nomination',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    print("\n🚀 测试nomination模板（不包含二维码）...")
    print(f"📋 模板: {headers['X-Html-Template']}")
    print(f"📝 数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
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
                print("✅ 渲染成功！（发送失败是预期的，二维码区域应该不显示）")
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 完整流程成功！")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 测试包含二维码的情况
    test_nomination_with_qr()
    
    # 测试不包含二维码的情况  
    test_nomination_without_qr()
    
    print("\n" + "="*50)
    print("📝 说明:")
    print("1. 第一个测试包含qr_code_base64参数，应该显示二维码")
    print("2. 第二个测试不包含qr_code_base64参数，二维码区域不应该显示")
    print("3. 这是Jinja2模板的条件渲染功能：{% if qr_code_base64 %}")