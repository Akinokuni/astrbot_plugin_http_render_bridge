#!/usr/bin/env python3
"""
HTTP Render Bridge Plugin API 测试脚本
用于测试插件的 HTTP API 接口功能
"""

import requests
import json
from datetime import datetime

# 配置
API_BASE_URL = "http://localhost:8080"
API_PATH = "/api/render/image"
AUTH_TOKEN = "your_token_here"  # 请替换为实际的认证令牌
TARGET_GROUP_ID = "123456789"   # 请替换为实际的群号
TARGET_USER_ID = "987654321"    # 请替换为实际的用户QQ号

def test_health_check():
    """测试健康检查端点"""
    print("🔍 测试健康检查端点...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_notification_template():
    """测试通知模板"""
    print("\n📧 测试通知模板...")
    
    url = f"{API_BASE_URL}{API_PATH}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "X-Html-Template": "notification",
        "X-Target-Type": "group",
        "X-Target-Id": TARGET_GROUP_ID
    }
    
    data = {
        "title": "系统通知",
        "content": "这是一条来自 HTTP Render Bridge 插件的测试通知消息。",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 通知模板测试失败: {e}")
        return False

def test_private_message():
    """测试私聊消息发送"""
    print("\n💬 测试私聊消息发送...")
    
    url = f"{API_BASE_URL}{API_PATH}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "X-Html-Template": "notification",
        "X-Target-Type": "private",
        "X-Target-Id": TARGET_USER_ID
    }
    
    data = {
        "title": "私聊测试",
        "content": "这是一条发送到私聊的测试消息。",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 私聊消息测试失败: {e}")
        return False

def test_authentication_error():
    """测试认证错误"""
    print("\n🔐 测试认证错误...")
    
    url = f"{API_BASE_URL}{API_PATH}"
    headers = {
        "Authorization": "Bearer wrong_token",
        "X-Html-Template": "notification",
        "X-Target-Type": "group",
        "X-Target-Id": TARGET_GROUP_ID
    }
    
    data = {
        "title": "测试",
        "content": "这条消息不应该被发送"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ 认证错误测试失败: {e}")
        return False

def test_missing_headers():
    """测试缺少必需头部"""
    print("\n📋 测试缺少必需头部...")
    
    url = f"{API_BASE_URL}{API_PATH}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        # 故意缺少 X-Html-Template
        "X-Target-Type": "group",
        "X-Target-Id": TARGET_GROUP_ID
    }
    
    data = {
        "title": "测试",
        "content": "这条消息不应该被发送"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 缺少头部测试失败: {e}")
        return False

def test_nonexistent_template():
    """测试不存在的模板"""
    print("\n🎨 测试不存在的模板...")
    
    url = f"{API_BASE_URL}{API_PATH}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "X-Html-Template": "nonexistent_template",
        "X-Target-Type": "group",
        "X-Target-Id": TARGET_GROUP_ID
    }
    
    data = {
        "title": "测试",
        "content": "这条消息不应该被发送"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400
    except Exception as e:
        print(f"❌ 不存在模板测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 HTTP Render Bridge Plugin API 测试开始")
    print("=" * 50)
    
    # 提醒用户配置
    print("⚠️  请确保:")
    print(f"   1. 插件已在 AstrBot 中启动")
    print(f"   2. HTTP 服务运行在 {API_BASE_URL}")
    print(f"   3. 已配置正确的认证令牌")
    print(f"   4. 已配置正确的目标群号/用户号")
    print()
    
    input("按 Enter 键开始测试...")
    
    tests = [
        ("健康检查", test_health_check),
        ("通知模板", test_notification_template),
        ("私聊消息", test_private_message),
        ("认证错误", test_authentication_error),
        ("缺少头部", test_missing_headers),
        ("不存在模板", test_nonexistent_template),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！插件工作正常。")
    else:
        print("⚠️  部分测试失败，请检查配置和日志。")

if __name__ == "__main__":
    main()