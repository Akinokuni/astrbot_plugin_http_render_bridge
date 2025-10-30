#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

# 测试API调用，使用正确的multipart格式
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
data = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="title"\r\n\r\n'
    f'Test Title\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="content"\r\n\r\n'
    f'Hello World Content\r\n'
    f'--{boundary}--\r\n'
).encode()

req = urllib.request.Request('http://localhost:8080/api/render/image', data=data, method='POST')
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
req.add_header('X-Html-Template', 'notification')
req.add_header('X-Target-Type', 'group')
req.add_header('X-Target-Id', '123456')

try:
    response = urllib.request.urlopen(req)
    print('Status:', response.getcode())
    print('Response:', response.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    print('Response:', e.read().decode())
except Exception as e:
    print('Error:', e)