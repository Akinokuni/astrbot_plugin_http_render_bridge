import asyncio
import base64
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import quote

import aiohttp
from aiohttp import web, MultipartReader

from astrbot.api import logger
from astrbot.api.star import Context, Star, register
from astrbot.core.config import AstrBotConfig

# Typst 渲染引擎：官方 Python 绑定为主渲染路径
# 绑定不可用时回退到系统安装的 typst CLI（见 _compile_typst_with_cli）
try:
    import typst
    TYPST_BINDING_AVAILABLE = True
except ImportError:
    typst = None
    TYPST_BINDING_AVAILABLE = False

# 渲染质量档位到 PPI 的映射（PPI 决定输出像素宽度：页面宽度(pt) / 72 × PPI）
QUALITY_PPI_MAP = {
    'low': 72,
    'medium': 144,
    'high': 200,
    'ultra': 300,
}
DEFAULT_QUALITY = 'high'


def _compile_typst_with_binding(source: str, ppi: int, data_json: str) -> bytes:
    """使用官方 typst Python 绑定在内存中编译模板为 PNG（主渲染路径）

    :param source: Typst 模板源码
    :param ppi: 输出图片的 PPI
    :param data_json: 注入模板的数据（sys.inputs 的 data 参数）
    :return: PNG 图片字节
    """
    png_bytes = typst.compile(
        source.encode('utf-8'),
        format='png',
        ppi=ppi,
        sys_inputs={'data': data_json},
    )
    return bytes(png_bytes)


async def _compile_typst_with_cli(source: str, ppi: int, data_json: str) -> bytes:
    """使用 typst CLI 子进程编译模板为 PNG（后备渲染路径）

    模板源码通过 stdin（输入 `-`）传递，PNG 从 stdout（输出 `-`）读取，
    不落盘临时文件。data 参数通过 --input 直接传入 argv，不经过 shell。
    """
    proc = await asyncio.create_subprocess_exec(
        'typst', 'compile',
        '--format', 'png',
        '--ppi', str(ppi),
        '--input', f'data={data_json}',
        '-', '-',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate(source.encode('utf-8'))
    if proc.returncode != 0:
        error_detail = stderr.decode('utf-8', errors='replace').strip()
        raise RuntimeError(f'typst CLI 编译失败: {error_detail}')
    return stdout


async def fetch_qr_code_as_hex(url: str) -> str:
    """从在线API获取二维码图片，返回hex字符串（模板通过hex-to-bytes解码为图片）"""
    try:
        # 构建二维码API URL
        encoded_url = quote(url, safe='')
        qr_api_url = f"https://api.2dcode.biz/v1/create-qr-code?data={encoded_url}"
        
        async with aiohttp.ClientSession() as session:
            # 添加超时防止挂起
            async with session.get(qr_api_url, timeout=10) as response:
                response.raise_for_status()
                image_data = await response.read()
                hex_image = image_data.hex()
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 二维码hex字符串长度: {len(hex_image)}")
                return hex_image
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
        
        # 检查文件扩展名（Typst 支持 png/jpg/gif/webp/svg）
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 不支持的图片格式: {file_ext}")
            return None
        
        # 转换为hex字符串（Typst模板通过hex-to-bytes解码）
        hex_data = file_data.hex()
        
        return {
            'filename': filename,
            'size': len(file_data),
            'hex': hex_data
        }
        
    except Exception as e:
        logger.error(f"[AstrBot Plugin HTTP Render Bridge] 处理图片文件失败: {e}")
        return None


@register(
    'astrbot_plugin_http_render_bridge',
    'Kiro AI Assistant',
    'HTTP Render Bridge Plugin',
    '2.0.0',
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
        """重新加载模板缓存：扫描 templates/ 目录的 .typ 文件 + 配置中的自定义模板"""
        self.templates_cache.clear()

        # 获取插件目录路径
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(plugin_dir, 'templates')

        # 自动扫描templates目录下的所有Typst模板文件
        if os.path.exists(templates_dir):
            try:
                for filename in os.listdir(templates_dir):
                    if filename.endswith('.typ'):
                        template_name = filename[:-4]  # 移除.typ后缀
                        template_file = os.path.join(templates_dir, filename)

                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                typ_content = f.read()

                            self.templates_cache[template_name] = {
                                'typ_content': typ_content,
                                'name': f'{template_name.title()}模板',
                                'description': f'基于{filename}的Typst模板',
                                'file': filename,
                                'render_quality': DEFAULT_QUALITY,
                            }
                            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 已加载模板: {template_name} ({filename})")

                        except Exception as e:
                            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 加载模板文件 {filename} 失败: {e}")

            except Exception as e:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 扫描模板目录失败: {e}")
        else:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板目录不存在: {templates_dir}")

        # 加载配置中的自定义模板（typ_content 字段）
        custom_templates = self.config.get('templates', {})
        if isinstance(custom_templates, dict):
            for alias, tpl in custom_templates.items():
                if isinstance(tpl, dict) and tpl.get('typ_content'):
                    self.templates_cache[alias] = {
                        'typ_content': tpl['typ_content'],
                        'name': tpl.get('name', f'{alias}模板'),
                        'description': tpl.get('description', '自定义Typst模板'),
                        'file': f'{alias}.typ',
                        'render_quality': tpl.get('render_quality', DEFAULT_QUALITY),
                    }
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 已加载自定义模板: {alias}")

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
                'file': info.get('file', f'{name}.typ'),
                'description': info.get('description', '')
            })
        
        return web.json_response({
            'status': 'ok',
            'plugin': 'astrbot_plugin_http_render_bridge',
            'version': '2.0.0',
            'render_engine': 'Typst',
            'templates_count': len(self.templates_cache),
            'available_templates': available_templates,
            'timestamp': datetime.now().isoformat()
        })

    async def render_handler(self, request: web.Request):
        """主要的消息处理器 - 支持Typst模板渲染和直接消息发送"""
        try:
            # 1. 认证检查
            auth_result = self._check_authentication(request)
            if auth_result:
                return auth_result

            # 2. 检查消息类型
            message_type = request.headers.get('X-Message-Type', 'template')

            if message_type == 'template':
                # Typst模板渲染模式
                return await self._handle_template_render(request)
            else:
                # 直接消息发送模式
                return await self._handle_direct_message(request, message_type)
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 处理请求时发生错误: {e}")
            return web.json_response({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)

    async def _handle_template_render(self, request: web.Request):
        """处理Typst模板渲染请求"""
        try:
            # 验证请求头
            headers_result = self._validate_headers(request)
            if isinstance(headers_result, web.Response):
                return headers_result

            template_alias, target_type, target_id = headers_result

            # 解析请求体
            form_data = await self._parse_form_data(request)
            if isinstance(form_data, web.Response):
                return form_data

            # 渲染图片（返回 PNG 字节）
            image_bytes = await self._render_template_to_image(template_alias, form_data)
            if not image_bytes:
                return web.json_response({
                    'status': 'error',
                    'message': 'Failed to render template to image'
                }, status=500)

            # 发送消息
            send_result = await self._send_message(target_type, target_id, image_bytes)
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
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 模板渲染处理失败: {e}")
            return web.json_response({
                'status': 'error',
                'message': 'Template render failed'
            }, status=500)

    async def _handle_direct_message(self, request: web.Request, message_type: str):
        """处理直接消息发送请求"""
        try:
            # 验证基本请求头（不需要模板）
            target_type = request.headers.get('X-Target-Type')
            target_id = request.headers.get('X-Target-Id')
            
            if not target_type or not target_id:
                return web.json_response({
                    'status': 'error',
                    'message': 'Missing X-Target-Type or X-Target-Id header'
                }, status=400)
            
            if target_type not in ['group', 'private']:
                return web.json_response({
                    'status': 'error',
                    'message': "X-Target-Type must be 'group' or 'private'"
                }, status=400)
            
            # 解析请求体
            form_data = await self._parse_form_data(request)
            if isinstance(form_data, web.Response):
                return form_data
            
            # 构建消息内容
            message_content = await self._build_message_content(message_type, form_data)
            if not message_content:
                return web.json_response({
                    'status': 'error',
                    'message': f'Failed to build message content for type: {message_type}'
                }, status=400)
            
            # 发送消息
            send_result = await self._send_direct_message(target_type, target_id, message_content)
            if not send_result:
                return web.json_response({
                    'status': 'error',
                    'message': 'Failed to send message to target'
                }, status=500)
            
            return web.json_response({
                'status': 'success',
                'message': f'{message_type.title()} message sent successfully',
                'message_type': message_type,
                'target': f"{target_type}:{target_id}"
            })
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 直接消息处理失败: {e}")
            return web.json_response({
                'status': 'error',
                'message': 'Direct message failed'
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
        # 检查X-Template
        template_name = request.headers.get('X-Template')
        if not template_name:
            return web.json_response({
                'status': 'error',
                'message': "Header 'X-Template' is missing"
            }, status=400)

        # 如果包含.typ后缀，移除它
        if template_name.endswith('.typ'):
            template_name = template_name[:-4]

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
                            # 使用字段名作为键，存储图片的hex数据
                            form_data[field.name] = file_info['hex']
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

    async def _render_template_to_image(self, template_alias: str, data: Dict[str, Any]) -> Optional[bytes]:
        """渲染Typst模板为PNG图片字节

        数据注入方式：请求体数据聚合为 JSON 字符串，通过 sys.inputs 的
        data 单一入口注入模板（模板内使用 json(bytes(...)) 解析）。
        """
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

                qr_hex = await fetch_qr_code_as_hex(link_url)
                if qr_hex:
                    render_data['qr_code'] = qr_hex
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 二维码生成成功，已添加到渲染数据")
                else:
                    logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 二维码生成失败，将不显示二维码")

            # 请求体数据聚合为 JSON 字符串（sys.inputs 的 data 单一入口）
            data_json = json.dumps(render_data, ensure_ascii=False)

            source = template_info['typ_content']
            quality = template_info.get('render_quality', DEFAULT_QUALITY)
            ppi = QUALITY_PPI_MAP.get(quality, QUALITY_PPI_MAP[DEFAULT_QUALITY])

            # 主渲染路径：官方 typst Python 绑定（内存编译）
            if TYPST_BINDING_AVAILABLE:
                try:
                    logger.info(f"[AstrBot Plugin HTTP Render Bridge] 使用 typst Python 绑定渲染（{quality}, {ppi} PPI）")
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(None, _compile_typst_with_binding, source, ppi, data_json)
                except Exception as binding_error:
                    logger.warning(f"[AstrBot Plugin HTTP Render Bridge] typst Python 绑定渲染失败，回退 CLI: {binding_error}")

            # 后备渲染路径：typst CLI 子进程
            try:
                logger.info(f"[AstrBot Plugin HTTP Render Bridge] 使用 typst CLI 渲染（{quality}, {ppi} PPI）")
                return await _compile_typst_with_cli(source, ppi, data_json)
            except FileNotFoundError:
                logger.error("[AstrBot Plugin HTTP Render Bridge] typst CLI 不可用且 Python 绑定未安装，模板渲染模式不可用")
                return None
            except Exception as cli_error:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] typst CLI 渲染失败: {cli_error}")
                return None

        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 渲染图片时发生错误: {e}")
            return None

    async def _send_message(self, target_type: str, target_id: str, image_bytes: bytes) -> bool:
        """将渲染出的PNG图片字节发送到指定目标"""
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
            if not image_bytes:
                logger.error(f"[AstrBot Plugin HTTP Render Bridge] 渲染返回空结果")
                return False

            # PNG字节转换为OneBot的base64数据格式
            base64_data = base64.b64encode(image_bytes).decode('utf-8')
            file_data = f"base64://{base64_data}"
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 准备发送图片，大小: {len(image_bytes)} bytes")

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

    async def _build_message_content(self, message_type: str, form_data: Dict[str, Any]):
        """根据消息类型构建消息内容"""
        try:
            if message_type == 'text':
                # 纯文本消息
                text = form_data.get('text', form_data.get('content', ''))
                if not text:
                    return None
                return [{'type': 'text', 'data': {'text': text}}]
            
            elif message_type == 'image':
                # 图片消息
                if 'image' in form_data:
                    return [{'type': 'image', 'data': {'file': form_data['image']}}]
                elif 'url' in form_data:
                    return [{'type': 'image', 'data': {'file': form_data['url']}}]
                return None
            
            elif message_type == 'voice':
                # 语音消息
                if 'voice' in form_data:
                    return [{'type': 'record', 'data': {'file': form_data['voice']}}]
                elif 'url' in form_data:
                    return [{'type': 'record', 'data': {'file': form_data['url']}}]
                return None
            
            elif message_type == 'video':
                # 视频消息
                if 'video' in form_data:
                    return [{'type': 'video', 'data': {'file': form_data['video']}}]
                elif 'url' in form_data:
                    return [{'type': 'video', 'data': {'file': form_data['url']}}]
                return None
            
            elif message_type == 'at':
                # @消息
                text = form_data.get('text', '')
                qq = form_data.get('qq', form_data.get('user_id', ''))
                if not qq:
                    return None
                
                message = []
                if qq == 'all':
                    message.append({'type': 'at', 'data': {'qq': 'all'}})
                else:
                    message.append({'type': 'at', 'data': {'qq': str(qq)}})
                
                if text:
                    message.append({'type': 'text', 'data': {'text': f' {text}'}})
                
                return message
            
            elif message_type == 'reply':
                # 回复消息
                message_id = form_data.get('message_id', form_data.get('id', ''))
                text = form_data.get('text', form_data.get('content', ''))
                
                if not message_id:
                    return None
                
                message = [{'type': 'reply', 'data': {'id': str(message_id)}}]
                if text:
                    message.append({'type': 'text', 'data': {'text': text}})
                
                return message
            
            elif message_type == 'forward':
                # 转发消息
                message_id = form_data.get('message_id', form_data.get('id', ''))
                if not message_id:
                    return None
                return [{'type': 'forward', 'data': {'id': str(message_id)}}]
            
            elif message_type == 'face':
                # 表情消息
                face_id = form_data.get('face_id', form_data.get('id', ''))
                if not face_id:
                    return None
                return [{'type': 'face', 'data': {'id': str(face_id)}}]
            
            elif message_type == 'poke':
                # 戳一戳
                qq = form_data.get('qq', form_data.get('user_id', ''))
                if not qq:
                    return None
                return [{'type': 'poke', 'data': {'qq': str(qq)}}]
            
            elif message_type == 'shake':
                # 窗口抖动
                return [{'type': 'shake', 'data': {}}]
            
            elif message_type == 'music':
                # 音乐分享
                music_type = form_data.get('type', '163')  # 默认网易云音乐
                music_id = form_data.get('id', '')
                if not music_id:
                    return None
                return [{'type': 'music', 'data': {'type': music_type, 'id': str(music_id)}}]
            
            elif message_type == 'share':
                # 链接分享
                url = form_data.get('url', '')
                title = form_data.get('title', '')
                content = form_data.get('content', form_data.get('description', ''))
                image = form_data.get('image', '')
                
                if not url:
                    return None
                
                share_data = {'url': url}
                if title:
                    share_data['title'] = title
                if content:
                    share_data['content'] = content
                if image:
                    share_data['image'] = image
                
                return [{'type': 'share', 'data': share_data}]
            
            elif message_type == 'location':
                # 位置分享
                lat = form_data.get('lat', form_data.get('latitude', ''))
                lon = form_data.get('lon', form_data.get('longitude', ''))
                title = form_data.get('title', '')
                content = form_data.get('content', form_data.get('address', ''))
                
                if not lat or not lon:
                    return None
                
                location_data = {'lat': str(lat), 'lon': str(lon)}
                if title:
                    location_data['title'] = title
                if content:
                    location_data['content'] = content
                
                return [{'type': 'location', 'data': location_data}]
            
            elif message_type == 'mixed':
                # 混合消息（文本+图片等）
                message = []
                
                # 添加文本
                if 'text' in form_data or 'content' in form_data:
                    text = form_data.get('text', form_data.get('content', ''))
                    if text:
                        message.append({'type': 'text', 'data': {'text': text}})
                
                # 添加图片
                if 'image' in form_data:
                    message.append({'type': 'image', 'data': {'file': form_data['image']}})
                
                # 添加@用户
                if 'at' in form_data:
                    at_qq = form_data['at']
                    if at_qq == 'all':
                        message.append({'type': 'at', 'data': {'qq': 'all'}})
                    else:
                        message.append({'type': 'at', 'data': {'qq': str(at_qq)}})
                
                return message if message else None
            
            else:
                logger.warning(f"[AstrBot Plugin HTTP Render Bridge] 不支持的消息类型: {message_type}")
                return None
                
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 构建消息内容失败: {e}")
            return None

    async def _send_direct_message(self, target_type: str, target_id: str, message_content):
        """发送直接消息"""
        try:
            # 获取平台实例
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
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 准备发送直接消息: {message_content}")
            
            # 根据目标类型发送消息
            if target_type == 'group':
                await client.send_group_msg(group_id=int(target_id), message=message_content)
            else:
                await client.send_private_msg(user_id=int(target_id), message=message_content)
            
            logger.info(f"[AstrBot Plugin HTTP Render Bridge] 成功发送直接消息到 {target_type}:{target_id}")
            return True
            
        except Exception as e:
            logger.error(f"[AstrBot Plugin HTTP Render Bridge] 发送直接消息失败: {e}")
            return False

    async def terminate(self):
        """插件终止时的清理工作"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("[AstrBot Plugin HTTP Render Bridge] HTTP服务器已停止")