from astrbot.api.star import Context, Star, register
from astrbot.core.config import AstrBotConfig
from astrbot.api import logger
from typing import Optional

@register(
    'test_plugin',
    'Test Author',
    'Test Plugin',
    '1.0.0'
)
class TestPlugin(Star):
    def __init__(self, context: Context, config: Optional[AstrBotConfig] = None):
        super().__init__(context)
        logger.info("Test plugin loaded successfully!")