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
    'HTTP渲染桥梁插件 - 将结构化HTTP请求数据动态转化为图片并发送到QQ',
    '1.0.0'
)
class HttpRenderBridge(Star):
    def __init__(self, context: Context, config: Optional[AstrBotConfig] = None):
        super().__init__(context)
        self.config = config or AstrBotConfig({})
        self.runner: Optional[web.AppRunner] = None
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        
        # 初始化默认模板
        self._init_default_templates()
        
        # 启动HTTP服务器
        asyncio.create_task(self.start_server())

    def _init_default_templates(self):
        """初始化默认模板到配置中"""
        default_templates = self.config.get('default_templates', {})
        current_templates = self.config.get('templates', {})
        
        # 合并默认模板到当前模板配置中
        for alias, template_config in default_templates.items():
            if alias not in current_templates:
                current_templates[alias] = template_config
        
        self.config['templates'] = current_templates
        self.config.save_config()
        
        # 缓存模板
        self._reload_templates()

    def _reload_templates(self):
        """重新加载模板缓存"""
        self.templates_cache.clear()
        templates_config = self.config.get('templates', {})
        
        for alias, template_config in templates_config.items():
            try:
                html_content = template_config.get('html_content', '')
                if html_content:
                    self.templates_cache[alias] = {
                        'template': Template(html_content),
                        'render_width': template_config.get('render_width', 800),
                        'render_quality': template_config.get('render_quality', 'high'),
                        'name': template_config.get('name', alias),
                        'description': template_config.get('description', '')
                    }
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 已加载模板: {alias} ({template_config.get('name', alias)})")
            except Exception as e:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 加载模板 {alias} 失败: {e}")

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
            port = self.config.get('server_port', 8080)
            
            site = web.TCPSite(self.runner, host, port)
            await site.start()
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 服务器已启动: http://{host}:{port}{api_path}")
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 启动服务器失败: {e}")

    async def health_handler(self, request: web.Request):
        """健康检查处理器"""
        return web.json_response({
            'status': 'ok',
            'plugin': 'astrbot_plugin_http_render_bridge',
            'version': '1.0.0',
            'templates_count': len(self.templates_cache),
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
        template_alias = request.headers.get('X-Html-Template')
        if not template_alias:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Html-Template' is missing"
            }, status=400)
        
        if template_alias not in self.templates_cache:
            return web.json_response({
                'status': 'error',
                'message': f"Template '{template_alias}' not found"
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
        
        return template_alias, target_type, target_id

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
        """渲染模板为图片"""
        try:
            template_info = self.templates_cache.get(template_alias)
            if not template_info:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板 {template_alias} 不存在")
                return None
            
            # 渲染HTML
            template = template_info['template']
            html_content = template.render(**data)
            
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
            
            # 使用AstrBot的html_render功能
            image_url = await self.html_render(html_content, {}, options=render_options)
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 成功渲染模板 {template_alias} 为图片: {image_url}")
            return image_url
            
        except TemplateError as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板渲染错误: {e}")
            return None
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 渲染图片时发生错误: {e}")
            return None

    async def _send_message(self, target_type: str, target_id: str, image_url: str) -> bool:
        """发送消息到指定目标"""
        try:
            # 构建统一消息源标识符
            if target_type == 'group':
                unified_msg_origin = f"group_{target_id}"
            else:
                unified_msg_origin = f"private_{target_id}"
            
            # 创建消息链
            from astrbot.api.event import MessageChain
            import astrbot.api.message_components as Comp
            
            message_chain = MessageChain()
            message_chain.chain = [Comp.Image.fromURL(image_url)]
            
            # 发送消息
            await self.context.send_message(unified_msg_origin, message_chain)
            
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