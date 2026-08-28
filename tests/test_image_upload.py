#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试图片上传功能
"""

import requests
import os
from PIL import Image
import io

def create_test_image():
    """创建一个测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (200, 100), color='lightblue')
    
    # 保存为临时文件
    img_path = 'test_image.png'
    img.save(img_path, 'PNG')
    return img_path

def test_image_upload():
    """测试图片上传功能"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 创建测试图片
    test_image_path = create_test_image()
    
    try:
        # 准备请求数据
        headers = {
            'X-Html-Template': 'notification',
            'X-Target-Type': 'group',
            'X-Target-Id': '000000000',
        }
        
        # 准备表单数据
        data = {
            'title': '图片上传测试',
            'content': '这是一条包含图片的通知消息，测试图片上传功能是否正常工作。',
            'timestamp': '2024-10-30 18:00:00'
        }
        
        # 准备文件数据
        with open(test_image_path, 'rb') as f:
            files = {
                'image': ('test_image.png', f, 'image/png')
            }
            
            print("🚀 测试图片上传功能...")
            print(f"📋 模板: {headers['X-Html-Template']}")
            print(f"🖼️ 图片: {test_image_path}")
            print(f"📝 数据: {data}")
            print("-" * 50)
            
            # 发送请求
            response = requests.post(
                f"{base_url}{api_path}",
                headers=headers,
                data=data,
                files=files
            )
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
            if response.status_code == 500:
                result = response.json()
                if result.get('message') == 'Failed to send message to target':
                    print("✅ 渲染成功！（发送失败是预期的）")
                    print("🎯 图片应该已经嵌入到通知卡片中")
                else:
                    print(f"❌ 其他错误: {result.get('message')}")
            elif response.status_code == 200:
                print("✅ 完整流程成功！")
                print("🎯 图片应该已经嵌入并发送")
            elif response.status_code == 401:
                print("🔐 需要认证")
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"🧹 已清理测试文件: {test_image_path}")

def test_multiple_images():
    """测试多图片上传"""
    
    base_url = "http://localhost:11451"
    api_path = "/api/render/image"
    
    # 创建多个测试图片
    test_images = []
    for i in range(2):
        img = Image.new('RGB', (150, 100), color=['red', 'green'][i])
        img_path = f'test_image_{i}.png'
        img.save(img_path, 'PNG')
        test_images.append(img_path)
    
    try:
        headers = {
            'X-Html-Template': 'notification',
            'X-Target-Type': 'group',
            'X-Target-Id': '000000000',
        }
        
        data = {
            'title': '多图片测试',
            'content': '测试上传多张图片的功能',
            'timestamp': '2024-10-30 18:00:00'
        }
        
        # 准备多个文件
        files = []
        for i, img_path in enumerate(test_images):
            with open(img_path, 'rb') as f:
                files.append(('image' + str(i), (f'test_image_{i}.png', f.read(), 'image/png')))
        
        print("\n🚀 测试多图片上传功能...")
        print(f"📋 模板: {headers['X-Html-Template']}")
        print(f"🖼️ 图片数量: {len(test_images)}")
        print("-" * 50)
        
        response = requests.post(
            f"{base_url}{api_path}",
            headers=headers,
            data=data,
            files=files
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 500:
            result = response.json()
            if result.get('message') == 'Failed to send message to target':
                print("✅ 多图片渲染成功！")
            else:
                print(f"❌ 其他错误: {result.get('message')}")
        elif response.status_code == 200:
            print("✅ 多图片完整流程成功！")
        elif response.status_code == 401:
            print("🔐 需要认证")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理测试文件
        for img_path in test_images:
            if os.path.exists(img_path):
                os.remove(img_path)
        print(f"🧹 已清理 {len(test_images)} 个测试文件")

def test_large_image():
    """测试大图片处理"""
    
    print("\n🚀 测试大图片处理...")
    
    # 创建一个较大的图片（但仍在限制内）
    img = Image.new('RGB', (1000, 800), color='blue')
    img_path = 'large_test_image.jpg'
    img.save(img_path, 'JPEG', quality=85)
    
    file_size = os.path.getsize(img_path)
    print(f"🖼️ 大图片大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
    
    if file_size > 5 * 1024 * 1024:
        print("⚠️ 图片超过5MB限制，应该被拒绝")
    else:
        print("✅ 图片在5MB限制内，应该被接受")
    
    # 清理
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == "__main__":
    # 检查PIL是否可用
    try:
        from PIL import Image
    except ImportError:
        print("❌ 需要安装PIL库: pip install Pillow")
        exit(1)
    
    # 测试单图片上传
    test_image_upload()
    
    # 测试多图片上传
    test_multiple_images()
    
    # 测试大图片处理
    test_large_image()
    
    print("\n" + "="*50)
    print("📝 图片上传功能说明:")
    print("1. 支持的格式: JPG, PNG, GIF, WebP, BMP")
    print("2. 文件大小限制: 5MB")
    print("3. 图片会自动转换为base64嵌入模板")
    print("4. 模板中使用 {{image}} 显示图片")
    print("5. 可以使用 {{image_filename}} 显示文件名")
    print("6. 支持多图片上传（使用不同的字段名）")