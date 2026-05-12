"""
LLM 集成模块 - LLM Integration

封装私有大语言模型 API 调用，提供：
    - client: API 客户端适配器
    - context: 上下文窗口管理
    - prompts: 提示词模板管理

使用示例:
    from src.llm.client import LLMClient
    from src.llm.context import ContextManager

    client = LLMClient(config)
    response = client.complete("Translate this C function to Java...")
"""

from . import client
from . import context
from . import prompts

__all__ = ["client", "context", "prompts"]
