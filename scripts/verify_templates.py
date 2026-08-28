"""临时脚本：验证 templates/ 下所有 .typ 模板能否编译（含图片注入路径）"""
import base64
import json
import os
import sys

import typst

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

# 1x1 像素 PNG 的 hex 字符串，用于验证 image() 图片注入路径
TINY_PNG_HEX = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ'
    'AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
).hex()

sample_data = {
    "title": "测试通知",
    "content": "这是一条测试内容，包含中文标点、English words、数字123。",
    "timestamp": "2026-08-28 12:00:00",
    "name": "测试用户",
    "header": "十二器：提名",
    "title1": "测试作品一",
    "evaluate1": "推荐语一",
    "title2": "测试作品二",
    "evaluate2": "推荐语二",
    "title3": "测试作品三",
    "evaluate3": "推荐语三",
    "level": "WARNING",
    "message": "测试消息",
    "total_users": "1000",
    "active_users": "500",
    "new_users": "100",
    "total_messages": "9999",
    "qq_number": "123456789",
    "score": "80",
    "threshold": "60",
    "non_qq_subjective_text": "测试简答题回答内容",
    "submitted_at": "2026-08-28 11:00:00",
    "description": "图片展示测试",
    "image": TINY_PNG_HEX,
    "image_filename": "test.png",
    "image0": TINY_PNG_HEX,
    "image0_filename": "test0.png",
    "image1": TINY_PNG_HEX,
    "image1_filename": "test1.png",
    "qr_code": TINY_PNG_HEX,
    "qr_text": "扫码访问链接",
}

failures = 0
for filename in sorted(os.listdir(TEMPLATES_DIR)):
    if not filename.endswith('.typ'):
        continue
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    try:
        png = typst.compile(
            source.encode('utf-8'),
            format='png',
            ppi=72,
            sys_inputs={'data': json.dumps(sample_data, ensure_ascii=False)},
        )
        size = len(bytes(png)) if png else 0
        print(f"OK   {filename}: {size} bytes")
    except Exception as e:
        failures += 1
        print(f"FAIL {filename}: {type(e).__name__}: {e}")

print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILED'}")
sys.exit(1 if failures else 0)
