import asyncio
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from aiohttp import web, MultipartReader
from jinja2 import Template, TemplateError

from astrbot.api import logger
from astrbot.api.star import Context, Star, register
from astrbot.core.config import AstrBotConfig


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
        
        # 获取默认配置
        default_width = self.config.get('render_width', 800)
        default_quality = self.config.get('render_quality', 'high')
        
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
                                'render_width': default_width,
                                'render_quality': default_quality,
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
        """解析multipart/form-data请求体"""
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
            
            # 渲染HTML
            template = template_info['template']
            html_content = template.render(**data)
            
            # 直接使用HTML进行本地渲染，保留所有样式
            try:
                # 设置渲染选项
                render_options = {
                    'full_page': True,
                    'type': 'png'
                }
                
                quality = template_info.get('render_quality', 'high')
                if quality == 'high':
                    render_options['quality'] = 95
                elif quality == 'medium':
                    render_options['quality'] = 75
                else:
                    render_options['quality'] = 50
                
                # 强制使用本地渲染，跳过网络渲染
                try:
                    # 尝试直接调用本地渲染策略
                    from astrbot.core.t2i.local_strategy import LocalStrategy
                    local_renderer = LocalStrategy()
                    image_path = await local_renderer.render(html_content)
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 强制本地渲染成功: {image_path}")
                    return image_path
                except ImportError:
                    # 如果无法直接导入本地策略，使用原方法但设置强制本地渲染
                    image_path = await self.html_render(html_content, {}, return_url=False, options=render_options)
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] HTML本地渲染成功: {image_path}")
                    return image_path
                
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
            
            # 准备消息数据
            if image_path.startswith('http'):
                # 网络URL
                file_data = image_path
            else:
                # 检查文件是否存在
                if not os.path.exists(image_path):
                    logger.error(f"[AstrBot Plugin HTTP Render Bridge] 图片文件不存在: {image_path}")
                    return False
                
                # 获取绝对路径
                abs_path = os.path.abspath(image_path)
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 图片文件路径: {abs_path}")
                
                # 尝试直接使用绝对路径，如果失败再尝试file://格式
                file_data = abs_path
            
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