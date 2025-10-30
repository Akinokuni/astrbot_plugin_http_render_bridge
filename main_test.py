"""
最简单的测试插件，用于验证基本的插件加载机制
"""
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register(
    'test_simple',
    'Test',
    'Simple test plugin',
    '1.0.0'
)
class TestSimple(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("Simple test plugin loaded successfully!")