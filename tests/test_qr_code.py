#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试二维码自动生成功能
"""

import requests
import json

def test_qr_code_generation():
    """测试传入link参数自动生成二维码"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试数据 - 包含link参数
    test_data = {
        'name': '测试用户',
        'title1': '最佳创意奖',
        'evaluate1': '这个项目展现了卓越的创新思维和技术实现能力',
        'title2': '团队协作奖', 
        'evaluate2': '在团队合作中表现出色，能够有效协调各方资源',
        'title3': '技术突破奖',
        'evaluate3': '在技术实现上有重大突破，为行业发展做出贡献',
        'link': 'https://github.com/Akinokuni/astrbot_plugin_http_render_bridge',  # 自动生成二维码
        'qr_text': '扫码查看项目'  # 可选的二维码文本
    }
    
    headers = {
        'X-Template': 'nomination',
        'X-Target-Type': 'group',
        'X-Target-Id': '000000000',
    }
    
    print("🚀 测试二维码自动生成功能...")
    print(f"📋 模板: {headers['X-Template']}")
    print(f"🔗 链接: {test_data['link']}")
    print(f"📝 数据: {json.dumps({k: v for k, v in test_data.items() if k != 'link'}, ensure_ascii=False, indent=2)}")
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
                print("🎯 二维码应该已经自动生成并显示在右上角")
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 完整流程成功！")
            print("🎯 二维码应该已经自动生成并显示")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_multiple_templates_with_qr():
    """测试多个模板的二维码功能"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 测试不同模板
    templates_to_test = [
        {
            'template': 'notification',
            'data': {
                'title': '系统通知',
                'content': '这是一条包含二维码的通知消息',
                'timestamp': '2024-10-30 16:00:00',
                'link': 'https://example.com/notification',
                'qr_text': '扫码查看详情'
            }
        },
        {
            'template': 'success',
            'data': {
                'title': '操作成功',
                'message': '您的操作已成功完成',
                'link': 'https://example.com/success',
                'qr_text': '扫码查看结果'
            }
        },
        {
            'template': 'alert',
            'data': {
                'title': '重要提醒',
                'message': '请及时处理相关事项',
                'link': 'https://example.com/alert'
                # 不提供qr_text，应该使用默认文本
            }
        }
    ]
    
    for i, test_case in enumerate(templates_to_test, 1):
        print(f"\n🚀 测试 {i}: {test_case['template']} 模板...")
        
        headers = {
            'X-Template': test_case['template'],
            'X-Target-Type': 'group',
            'X-Target-Id': '000000000',
        }
        
        print(f"📋 模板: {test_case['template']}")
        print(f"🔗 链接: {test_case['data'].get('link', '无')}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}{api_path}",
                headers=headers,
                files={k: (None, v) for k, v in test_case['data'].items()}
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            
            if response.status_code == 500:
                result = response.json()
                if result.get('message') == 'Failed to send message to target':
                    print("✅ 渲染成功！")
                else:
                    print(f"❌ 错误: {result.get('message')}")
            elif response.status_code == 200:
                print("✅ 完整流程成功！")
            elif response.status_code == 401:
                print("🔐 需要认证")
            else:
                print(f"❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    # 测试nomination模板的二维码功能
    test_qr_code_generation()
    
    # 测试多个模板的二维码功能
    test_multiple_templates_with_qr()
    
    print("\n" + "="*50)
    print("📝 二维码功能说明:")
    print("1. 传入 'link' 参数，插件会自动生成二维码")
    print("2. 可选传入 'qr_text' 参数自定义二维码下方文字")
    print("3. 如果不传入 'qr_text'，会使用默认文字 '扫码访问链接'")
    print("4. 二维码会显示在模板的右上角（如果模板支持）")
    print("5. 如果不传入 'link' 参数，二维码区域不会显示")