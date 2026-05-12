"""
LLM 客户端 - LLM Client

封装 OpenAI 兼容 API 的调用，支持：
    - 文本补全
    - 流式输出
    - 自动重试
    - 速率限制

使用示例:
    client = LLMClient(endpoint="http://localhost:8080/v1", api_key="xxx")
    response = client.complete(prompt)
"""

from .client import LLMClient, LLMResponse

__all__ = ["LLMClient", "LLMResponse"]
