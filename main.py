import asyncio
import base64
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import quote

import aiohttp
from aiohttp import web, MultipartReader
from jinja2 import Template, TemplateError

from astrbot.api import logger
from astrbot.api.star import Context, Star, register
from astrbot.core.config import AstrBotConfig


async def fetch_qr_code_as_base64(url: str) -> str:
    """从在线API获取二维码的base64编码（参考http_forwarder项目）"""
    try:
        # 构建二维码API URL
        encoded_url = quote(url, safe='')
        qr_api_url = f"https://api.2dcode.biz/v1/create-qr-code?data={encoded_url}"
        
        async with aiohttp.ClientSession() as session:
            # 添加超时防止挂起
            async with session.get(qr_api_url, timeout=10) as response:
                response.raise_for_status()
                image_data = await response.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 二维码Base64字符串长度: {len(encoded_image)}")
                return encoded_image
    except aiohttp.ClientError as e:
        logger.error(f"[AstrBot Plugin HTTP Render Bridge] 从 {url} 获取二维码时网络错误: {e}")
        return ""
    except asyncio.TimeoutError:
        logger.error(f"[AstrBot Plugin HTTP Render Bridge] 从 {url} 获取二维码超时")
        return ""
    except Exception as e:
        logger.error(f"[AstrBot Plugin HTTP Render Bridge] 从 {url} 获取二维码时发生意外错误: {e}")
        return ""


async def process_uploaded_image(filename: str, file_data: bytes) -> Optional[Dict[str, Any]]:
    """处理上传的图片文件"""
    try:
        # 检查文件大小（限制为5MB）
        max_size = 5 * 1024 * 1024  # 5MB
        if len(file_data) > max_size:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 图片文件过大: {len(file_data)} bytes > {max_size} bytes")
            return None
        
        # 检查文件扩展名
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 不支持的图片格式: {file_ext}")
            return None
        
        # 转换为base64
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # 确定MIME类型
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        mime_type = mime_types.get(file_ext, 'image/jpeg')
        
        return {
            'filename': filename,
            'size': len(file_data),
            'mime_type': mime_type,
            'base64': f"data:{mime_type};base64,{base64_data}"
        }
        
    except Exception as e:
        logger.error(f"[AstrBot Plugin HTTP Render Bridge] 处理图片文件失败: {e}")
        return None


@register(
    'astrbot_plugin_http_render_bridge',
    'Kiro AI Assistant',
    'HTTP Render Bridge Plugin',
    '1.0.0',
    'https://github.com/Akinokuni/astrbot_plugin_http_render_bridge'
)
class HttpRenderBridge(Star):
    def __init__(self, context: Context, config: Optional[AstrBotConfig] = None):
        super().__init__(context)
        # 使用传入的配置对象
        self.config = config or AstrBotConfig({})
        self.runner: Optional[web.AppRunner] = None
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info("[AstrBot Plugin HTTP Render Bridge] 插件初始化开始")
        
        # 初始化默认模板
        self._init_default_templates()
        
        # 启动HTTP服务器
        asyncio.create_task(self.start_server())
        
        logger.info("[AstrBot Plugin HTTP Render Bridge] 插件初始化完成")

    def _init_default_templates(self):
        """初始化默认模板"""
        self._reload_templates()

    def _reload_templates(self):
        """重新加载模板缓存"""
        self.templates_cache.clear()
        
        # 调试：打印配置内容
        logger.info(f"[AstrBot Plugin HTTP Render Bridge] 配置内容: {dict(self.config)}")
        
        # 获取插件目录路径
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(plugin_dir, 'templates')
        
        # 注意：render_width和render_quality参数已移除，因为AstrBot的html_render方法不支持这些选项
        
        # 自动扫描templates目录下的所有HTML文件
        if os.path.exists(templates_dir):
            try:
                for filename in os.listdir(templates_dir):
                    if filename.endswith('.html'):
                        template_name = filename[:-5]  # 移除.html后缀
                        template_file = os.path.join(templates_dir, filename)
                        
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            self.templates_cache[template_name] = {
                                'template': Template(html_content),
                                'name': f'{template_name.title()}模板',
                                'description': f'基于{filename}的模板',
                                'file': filename
                            }
                            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 已加载模板: {template_name} ({filename})")
                            
                        except Exception as e:
                            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 加载模板文件 {filename} 失败: {e}")
                            
            except Exception as e:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 扫描模板目录失败: {e}")
        else:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板目录不存在: {templates_dir}")
        
        # 确保至少有一个可用的模板
        if not self.templates_cache:
            logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 没有找到任何可用的模板文件")
        else:
            template_names = list(self.templates_cache.keys())
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 共加载 {len(template_names)} 个模板: {', '.join(template_names)}")

    async def start_server(self):
        """启动HTTP服务器"""
        try:
            app = web.Application()
            
            # 添加路由
            api_path = self.config.get('api_path', '/api/render/image')
            app.router.add_post(api_path, self.render_handler)
            
            # 添加健康检查端点
            app.router.add_get('/health', self.health_handler)
            
            self.runner = web.AppRunner(app)
            await self.runner.setup()
            
            host = self.config.get('server_host', '0.0.0.0')
            port = self.config.get('server_port', 11451)
            
            site = web.TCPSite(self.runner, host, port)
            await site.start()
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 服务器已启动: http://{host}:{port}{api_path}")
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 启动服务器失败: {e}")

    async def health_handler(self, request: web.Request):
        """健康检查处理器"""
        available_templates = []
        for name, info in self.templates_cache.items():
            available_templates.append({
                'name': name,
                'file': info.get('file', f'{name}.html'),
                'description': info.get('description', '')
            })
        
        return web.json_response({
            'status': 'ok',
            'plugin': 'astrbot_plugin_http_render_bridge',
            'version': '1.0.0',
            'templates_count': len(self.templates_cache),
            'available_templates': available_templates,
            'timestamp': datetime.now().isoformat()
        })

    async def render_handler(self, request: web.Request):
        """主要的渲染处理器"""
        try:
            # 1. 认证检查
            auth_result = self._check_authentication(request)
            if auth_result:
                return auth_result
            
            # 2. 验证请求头
            headers_result = self._validate_headers(request)
            if isinstance(headers_result, web.Response):
                return headers_result
            
            template_alias, target_type, target_id = headers_result
            
            # 3. 解析请求体
            form_data = await self._parse_form_data(request)
            if isinstance(form_data, web.Response):
                return form_data
            
            # 4. 渲染图片
            image_url = await self._render_template_to_image(template_alias, form_data)
            if not image_url:
                return web.json_response({
                    'status': 'error',
                    'message': 'Failed to render template to image'
                }, status=500)
            
            # 5. 发送消息
            send_result = await self._send_message(target_type, target_id, image_url)
            if not send_result:
                return web.json_response({
                    'status': 'error',
                    'message': 'Failed to send message to target'
                }, status=500)
            
            return web.json_response({
                'status': 'success',
                'message': 'Image sent successfully',
                'template_used': template_alias,
                'target': f"{target_type}:{target_id}"
            })
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 处理请求时发生错误: {e}")
            return web.json_response({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    def _check_authentication(self, request: web.Request) -> Optional[web.Response]:
        """检查Bearer Token认证"""
        auth_token = self.config.get('auth_token', '')
        if not auth_token:
            return None  # 如果没有配置token，跳过认证
        
        auth_header = request.headers.get('Authorization', '')
        expected_header = f"Bearer {auth_token}"
        
        if auth_header != expected_header:
            logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 认证失败: {auth_header}")
            return web.json_response({
                'status': 'error',
                'message': 'Unauthorized'
            }, status=401)
        
        return None

    def _validate_headers(self, request: web.Request):
        """验证必需的请求头"""
        # 检查X-Html-Template
        template_name = request.headers.get('X-Html-Template')
        if not template_name:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Html-Template' is missing"
            }, status=400)
        
        # 如果包含.html后缀，移除它
        if template_name.endswith('.html'):
            template_name = template_name[:-5]
        
        if template_name not in self.templates_cache:
            available_templates = list(self.templates_cache.keys())
            return web.json_response({
                'status': 'error',
                'message': f"Template '{template_name}' not found. Available templates: {', '.join(available_templates)}"
            }, status=400)
        
        # 检查X-Target-Type
        target_type = request.headers.get('X-Target-Type')
        if not target_type:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Target-Type' is missing"
            }, status=400)
        
        if target_type not in ['group', 'private']:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Target-Type' must be 'group' or 'private'"
            }, status=400)
        
        # 检查X-Target-Id
        target_id = request.headers.get('X-Target-Id')
        if not target_id:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Target-Id' is missing"
            }, status=400)
        
        return template_name, target_type, target_id

    async def _parse_form_data(self, request: web.Request):
        """解析multipart/form-data请求体，支持文本和图片文件"""
        try:
            if request.content_type != 'multipart/form-data':
                return web.json_response({
                    'status': 'error',
                    'message': 'Content-Type must be multipart/form-data'
                }, status=400)
            
            reader = await request.multipart()
            form_data = {}
            
            async for field in reader:
                if field.name:
                    # 检查是否是文件字段
                    if field.filename:
                        # 这是一个文件字段
                        file_data = await field.read()
                        file_info = await process_uploaded_image(field.filename, file_data)
                        if file_info:
                            # 使用字段名作为键，存储图片的base64数据
                            form_data[field.name] = file_info['base64']
                            # 同时存储文件信息
                            form_data[f"{field.name}_filename"] = file_info['filename']
                            form_data[f"{field.name}_size"] = file_info['size']
                            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 处理图片文件: {field.name} -> {file_info['filename']} ({file_info['size']} bytes)")
                        else:
                            logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 图片处理失败: {field.filename}")
                    else:
                        # 这是一个文本字段
                        value = await field.text()
                        form_data[field.name] = value
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 解析到表单数据: {list(form_data.keys())}")
            return form_data
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 解析表单数据失败: {e}")
            return web.json_response({
                'status': 'error',
                'message': 'Failed to parse form data'
            }, status=400)

    async def _render_template_to_image(self, template_alias: str, data: Dict[str, Any]) -> Optional[str]:
        """渲染模板为图片 - 直接使用HTML本地渲染"""
        try:
            template_info = self.templates_cache.get(template_alias)
            if not template_info:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板 {template_alias} 不存在")
                return None
            
            # 处理二维码生成
            render_data = data.copy()
            
            # 如果传入了link参数，自动生成二维码
            if 'link' in data and data['link']:
                link_url = data['link']
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 检测到link参数，生成二维码: {link_url}")
                
                qr_base64 = await fetch_qr_code_as_base64(link_url)
                if qr_base64:
                    render_data['qr_code_base64'] = qr_base64
                    # 如果没有提供qr_text，让模板使用自己的默认值
                    # 不在这里设置默认值，让Jinja2模板的default过滤器处理
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 二维码生成成功，已添加到渲染数据")
                else:
                    logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 二维码生成失败，将不显示二维码")
            
            # 渲染HTML
            template = template_info['template']
            html_content = template.render(**render_data)
            
            # 完全按照http_forwarder的方式进行渲染
            try:
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 尝试渲染HTML为图片")
                image_url = await self.html_render(html_content, data)
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] html_render返回URL: {image_url}")
                return image_url
                
            except Exception as render_error:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] HTML本地渲染失败: {render_error}")
                # 如果HTML渲染失败，尝试Markdown作为后备方案
                try:
                    markdown_content = self._html_to_markdown(html_content, data)
                    image_path = await self.html_render(markdown_content, {}, return_url=False)
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] Markdown后备渲染成功: {image_path}")
                    return image_path
                except Exception as fallback_error:
                    logger.error(f"[AstrBot Plugin HTTP Render Bridge] Markdown后备渲染也失败: {fallback_error}")
                    return None
            
        except TemplateError as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板渲染错误: {e}")
            return None
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 渲染图片时发生错误: {e}")
            return None

    def _html_to_markdown(self, html_content: str, data: Dict[str, Any]) -> str:
        """将HTML内容转换为Markdown格式，仅作为HTML渲染失败时的后备方案"""
        # 提取关键数据
        title = data.get('title', '通知')
        content = data.get('content', '这是一条通知消息')
        timestamp = data.get('timestamp', '刚刚')
        
        # 构建美观的Markdown作为后备方案
        markdown = f"""# 📢 {title}

---

{content}

---

🕒 **时间**: {timestamp}

---
*由 AstrBot HTTP 渲染桥梁插件生成（后备渲染）*"""
        
        return markdown

    async def _send_message(self, target_type: str, target_id: str, image_path: str) -> bool:
        """发送消息到指定目标"""
        try:
            # 获取平台实例（参考http_forwarder的做法）
            platforms = self.context.platform_manager.get_insts()
            if not platforms:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 没有找到可用的平台实例")
                return False
            
            # 使用第一个可用的平台实例
            platform_inst = platforms[0]
            client = platform_inst.get_client()
            
            if not client:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 平台客户端不可用")
                return False
            
            # 检查渲染结果
            if not image_path:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 渲染返回空结果")
                return False
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 准备发送图片: {image_path}")
            
            # 如果是本地文件路径，尝试转换为base64数据URI
            if not image_path.startswith('http') and os.path.exists(image_path):
                try:
                    import base64
                    with open(image_path, 'rb') as f:
                        image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    file_data = f"base64://{base64_data}"
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 转换为base64数据URI，长度: {len(base64_data)}")
                except Exception as e:
                    logger.warning(f"[AstrBot Plugin HTTP Render Bridge] base64转换失败，使用原路径: {e}")
                    file_data = image_path
            else:
                file_data = image_path
            
            # 构建OneBot v11格式的消息
            message_data = [{'type': 'image', 'data': {'file': file_data}}]
            
            # 根据目标类型发送消息
            if target_type == 'group':
                await client.send_group_msg(group_id=int(target_id), message=message_data)
            else:
                await client.send_private_msg(user_id=int(target_id), message=message_data)
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 成功发送图片到 {target_type}:{target_id}")
            return True
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 发送消息失败: {e}")
            return False

    async def terminate(self):
        """插件终止时的清理工作"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("[AstrBot Plugin HTTP Render Bridge] HTTP服务器已停止")