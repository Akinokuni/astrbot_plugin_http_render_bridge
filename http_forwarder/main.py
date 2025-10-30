import asyncio
import base64
import io
from typing import Optional

from aiohttp import web

from astrbot.api import logger
from astrbot.api.message_components import Plain # Keep Plain for potential error messages
from astrbot.api.star import Context, Star, register


from astrbot.core.config import AstrBotConfig
import aiohttp


import os

HTML_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'template.html')
with open(HTML_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

async def fetch_qr_code_as_base64(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            # Add a timeout to prevent hanging
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                image_data = await response.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                logger.info(f"[HTTP Image Forwarder] QR Code Base64 string length: {len(encoded_image)}")
                return encoded_image
    except aiohttp.ClientError as e:
        logger.error(f"[HTTP Image Forwarder] Network error fetching QR code from {url}: {e}")
        return ""
    except asyncio.TimeoutError:
        logger.error(f"[HTTP Image Forwarder] Timeout fetching QR code from {url}")
        return ""
    except Exception as e:
        logger.error(f"[HTTP Image Forwarder] An unexpected error occurred while fetching QR code from {url}: {e}")
        return ""

@register(
    'http_image_forwarder',
    'Gemini',
    'A plugin to forward messages from HTTP requests to a specified chat group, rendering text as images.',
    '1.1.0'
)
class HttpForwarder(Star):
    def __init__(self, context: Context, config: Optional[AstrBotConfig] = None):
        super().__init__(context)
        self.config = config
        self.runner: Optional[web.AppRunner] = None
        asyncio.create_task(self.start_server())

    async def start_server(self):
        app = web.Application()
        app.add_routes([web.post('/forward', self.forward_handler)])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.config.get('host'), self.config.get('port'))
        await site.start()
        logger.info(f"HTTP Forwarder server started on http://{self.config.get('host')}:{self.config.get('port')}")

    async def forward_handler(self, request: web.Request):
        if self.config.get('token') and request.headers.get('Authorization') != f"Bearer {self.config.get('token')}":
            return web.json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)

        try:
            # Parse form data instead of JSON
            data = await request.post()
            
            # Extract and log all 7 parameters
            name = data.get('name', 'N/A')
            title1 = data.get('title1', 'N/A')
            evaluate1 = data.get('evaluate1', 'N/A')
            title2 = data.get('title2', 'N/A')
            evaluate2 = data.get('evaluate2', 'N/A')
            title3 = data.get('title3', 'N/A')
            evaluate3 = data.get('evaluate3', 'N/A')

            logger.info(f"[HTTP Image Forwarder] Received Form Data:")
            logger.info(f"  Name: {name}")
            logger.info(f"  Title1: {title1}, Evaluate1: {evaluate1}")
            logger.info(f"  Title2: {title2}, Evaluate2: {evaluate2}")
            logger.info(f"  Title3: {title3}, Evaluate3: {evaluate3}")

            # Prepare data for HTML rendering
            qr_code_url = "https://api.2dcode.biz/v1/create-qr-code?data=https%3A%2F%2Facnrx9i4d67u.feishu.cn%2Fshare%2Fbase%2Fform%2FshrcnsQU8YSQr2iQSStqAZRvn6e"
            qr_code_base64 = await fetch_qr_code_as_base64(qr_code_url)

            render_data = {
                "name": name,
                "title1": title1,
                "evaluate1": evaluate1,
                "title2": title2,
                "evaluate2": evaluate2,
                "title3": title3,
                "evaluate3": evaluate3,
                "qr_code_base64": qr_code_base64,
            }

            # Fallback message for when HTML rendering fails
            fallback_message_text = (
                f"昵称: {name}\n"
                f"\n"
                f"提名一: {title1}\n"
                f"推荐语: {evaluate1}\n"
                f"\n"
                f"提名二: {title2}\n"
                f"推荐语: {evaluate2}\n"
                f"\n"
                f"提名三: {title3}\n"
                f"推荐语: {evaluate3}"
            )

            # Check if the data is empty (e.g., all N/A) for a basic check
            if name == 'N/A' and title1 == 'N/A' and title2 == 'N/A' and title3 == 'N/A':
                 logger.error("[HTTP Image Forwarder] No valid data received to render.")
                 return web.json_response({'status': 'error', 'message': 'No valid data received to render'}, status=400)

            platform_name = self.config.get('platform_name')
            self_id_from_config = self.config.get('self_id')
            group_id = self.config.get('group_id')

            if not all([platform_name, self_id_from_config, group_id]):
                logger.error("Plugin not configured correctly. Please set platform_name, self_id, and group_id.")
                return web.json_response({'status': 'error', 'message': 'Plugin not configured'}, status=500)

            platforms = self.context.platform_manager.get_insts()
            found_client = None # Initialize found_client outside the loop

            logger.info(f"[HTTP Image Forwarder] Debug: Searching for platform '{platform_name}' with self_id '{self_id_from_config}'")
            if not platforms:
                logger.info("[HTTP Image Forwarder] Debug: No platform instances found in platform_manager.")
            else:
                for p in platforms:
                    p_class_name_lower = p.__class__.__name__.lower()
                    logger.info(f"[HTTP Image Forwarder] Debug: Checking platform instance: {p_class_name_lower}")

                    if platform_name not in p_class_name_lower:
                        logger.info(f"[HTTP Image Forwarder] Debug: Class name '{p_class_name_lower}' does not contain '{platform_name}'. Skipping.")
                        continue

                    client = p.get_client()
                    if not client:
                        logger.info(f"[HTTP Image Forwarder] Debug: Platform '{p_class_name_lower}' has no active client. Skipping.")
                        continue

                    try:
                        login_info = await client.get_login_info()
                        actual_self_id = login_info.get('user_id')
                        logger.info(f"[HTTP Image Forwarder] Debug: Found client for '{p_class_name_lower}'. Actual Self ID: '{actual_self_id}' (type: {type(actual_self_id)}) ")

                        if actual_self_id and str(actual_self_id) == str(self_id_from_config):
                            logger.info(f"[HTTP Image Forwarder] Debug: Match found! Platform: {p_class_name_lower}, Self ID: {actual_self_id}")
                            found_client = client # Assign the client directly
                            break
                        else:
                            logger.info(f"[HTTP Image Forwarder] Debug: Self ID mismatch. Config: '{self_id_from_config}', Actual: '{actual_self_id}'")

                    except Exception as e:
                        logger.warning(f"[HTTP Image Forwarder] Debug: Could not get login info from platform {p_class_name_lower}: {e}")
                        continue

            if not found_client: # Check if a client was found
                logger.error(f"Could not find a matching platform instance for {platform_name} with self_id {self_id_from_config}")
                return web.json_response({'status': 'error', 'message': 'Target platform instance not found'}, status=400)

            # Convert HTML to image URL
            logger.info(f"[HTTP Image Forwarder] Attempting to render HTML to image.")
            image_url = await self.html_render(HTML_TEMPLATE, render_data)
            logger.info(f"[HTTP Image Forwarder] html_render returned URL: {image_url}")

            if not image_url:
                logger.error("[HTTP Image Forwarder] HTML rendering returned an empty or invalid URL. Sending plain text fallback.")
                await found_client.send_group_msg(group_id=int(group_id), message=[{'type': 'text', 'data': {'text': fallback_message_text}}])
                return web.json_response({'status': 'warning', 'message': 'Image rendering failed, sent plain text fallback'})

            # Send image message using OneBot v11 format
            logger.info(f"[HTTP Image Forwarder] Sending image message with URL: {image_url}")
            await found_client.send_group_msg(group_id=int(group_id), message=[{'type': 'image', 'data': {'file': image_url}}])

            return web.json_response({'status': 'success', 'message': 'Message forwarded as image'})
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.json_response({'status': 'error', 'message': 'Internal server error'}, status=500)

    async def terminate(self):
        if self.runner:
            await self.runner.cleanup()
            logger.info("HTTP Forwarder server stopped.")