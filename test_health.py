#!/usr/bin/env python3
"""
测试插件健康状态和可用模板
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:11451"
HEALTH_PATH = "/health"

def test_health():
    """测试健康检查端点"""
    url = f"{BASE_URL}{HEALTH_PATH}"
    
    print("🏥 测试健康检查端点")
    print(f"🔗 请求地址: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📥 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务健康!")
            print(f"📊 插件信息:")
            print(f"   - 插件名称: {data.get('plugin', 'N/A')}")
            print(f"   - 版本: {data.get('version', 'N/A')}")
            print(f"   - 模板数量: {data.get('templates_count', 0)}")
            print(f"   - 时间戳: {data.get('timestamp', 'N/A')}")
            
            templates = data.get('available_templates', [])
            if templates:
                print(f"\n📋 可用模板 ({len(templates)}个):")
                for template in templates:
                    name = template.get('name', 'N/A')
                    file = template.get('file', 'N/A')
                    desc = template.get('description', 'N/A')
                    print(f"   - {name} ({file}): {desc}")
            else:
                print("\n⚠️  没有找到可用模板")
                
            return True
        else:
            print(f"❌ 服务异常: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        print("💡 请确认:")
        print("   1. AstrBot已启动")
        print("   2. HTTP渲染桥梁插件已加载")
        print("   3. 服务监听在端口11451")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 HTTP渲染桥梁插件 - 健康检查测试")
    print("=" * 50)
    
    if test_health():
        print("\n🎉 健康检查通过! 可以开始API测试")
    else:
        print("\n💥 健康检查失败! 请检查服务状态")

if __name__ == "__main__":
    main()