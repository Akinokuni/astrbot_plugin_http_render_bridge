#!/usr/bin/env python3
"""
测试模板加载和渲染功能
"""

import os
import sys
import requests
import json

# 测试配置
BASE_URL = "http://localhost:11451"
API_PATH = "/api/render/image"
AUTH_TOKEN = "test_token_123"  # 请根据实际配置修改

def test_template(template_name, data):
    """测试指定模板的渲染"""
    url = f"{BASE_URL}{API_PATH}"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "X-Template": template_name,  # 模板别名（不含.typ后缀）
        "X-Target-Type": "group",
        "X-Target-Id": "123456789"
    }
    
    print(f"\n🧪 测试模板: {template_name}")
    print(f"📤 发送数据: {data}")
    
    try:
        # 使用files参数来确保multipart/form-data格式
        files = {key: (None, value) for key, value in data.items()}
        response = requests.post(url, headers=headers, files=files, timeout=30)
        print(f"📥 响应状态: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 测试成功!")
        else:
            print("❌ 测试失败!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试HTTP渲染桥梁插件模板功能")
    print(f"🔗 测试地址: {BASE_URL}{API_PATH}")
    
    # 测试通知模板
    test_template("notification", {
        "title": "系统通知",
        "content": "这是一条测试通知消息，用于验证通知模板的渲染功能。",
        "timestamp": "2024-01-01 12:00:00"
    })
    
    # 测试警告模板
    test_template("alert", {
        "title": "系统警告",
        "message": "检测到系统异常，请及时处理！",
        "timestamp": "2024-01-01 12:05:00",
        "level": "ERROR"
    })
    
    # 测试成功模板
    test_template("success", {
        "title": "操作成功",
        "message": "数据备份已成功完成，所有文件已安全保存。",
        "timestamp": "2024-01-01 12:10:00"
    })
    
    # 测试提名模板
    test_template("nomination", {
        "header": "十二🥥器：提名",
        "name": "张三",
        "title1": "最佳创意奖",
        "evaluate1": "创意十足，设计理念新颖，实现效果出色。",
        "title2": "最佳团队奖",
        "evaluate2": "团队协作能力强，沟通顺畅，执行力优秀。",
        "title3": "最佳技术奖",
        "evaluate3": "技术实力雄厚，代码质量高，架构设计合理。",
        "qr_text": "扫码参与提名"
    })
    
    # 测试报告模板
    test_template("report", {
        "title": "每日数据报告",
        "total_users": "1,234",
        "active_users": "856",
        "new_users": "42",
        "total_messages": "5,678",
        "timestamp": "2024-01-01 23:59:59"
    })
    
    print("\n🎯 所有测试完成!")

if __name__ == "__main__":
    main()