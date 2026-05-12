"""
上下文管理模块 - Context Management

管理 LLM 对话上下文，包括：
    - Token 计数和限制
    - 上下文截断
    - 上下文保存/加载

使用示例:
    ctx = ContextManager(max_tokens=4096)
    ctx.add_user_message("Hello")
    ctx.add_assistant_message("Hi there!")
"""

from .context import ContextManager

__all__ = ["ContextManager"]
