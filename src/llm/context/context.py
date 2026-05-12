"""
上下文管理器 - Context Manager Implementation
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """
    对话消息

    Attributes:
        role: 角色 (user/system/assistant)
        content: 消息内容
        token_count: token 数量
    """
    role: str
    content: str
    token_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


class ContextManager:
    """
    上下文管理器

    管理 LLM 对话上下文，自动处理 token 限制。

    功能:
        - 添加消息
        - Token 计数
        - 自动截断
        - 保存/加载
    """

    def __init__(self, max_tokens: int = 4096):
        """
        初始化上下文管理器

        Args:
            max_tokens: 最大 token 数
        """
        self.max_tokens = max_tokens
        self.messages: List[Message] = []
        self._current_tokens = 0

    def add_message(self, role: str, content: str) -> None:
        """
        添加消息

        Args:
            role: 角色
            content: 内容
        """
        token_count = self._estimate_tokens(content)
        message = Message(role=role, content=content, token_count=token_count)

        self.messages.append(message)
        self._current_tokens += token_count

        # 检查是否超出限制
        self._truncate_if_needed()

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.add_message("assistant", content)

    def add_system_message(self, content: str) -> None:
        """添加系统消息"""
        self.add_message("system", content)

    def _estimate_tokens(self, text: str) -> int:
        """
        估算 token 数量

        简单估算：每 4 个字符约 1 个 token
        """
        return len(text) // 4 + 1

    def _truncate_if_needed(self) -> None:
        """如果超出 token 限制，截断最早的消息"""
        while self._current_tokens > self.max_tokens and len(self.messages) > 1:
            # 保留第一个系统消息
            if self.messages[0].role == "system" and len(self.messages) > 1:
                removed = self.messages.pop(1)
            else:
                removed = self.messages.pop(0)

            self._current_tokens -= removed.token_count
            logger.debug(f"Truncated message: {removed.token_count} tokens")

    def clear(self) -> None:
        """清空上下文"""
        self.messages.clear()
        self._current_tokens = 0

    @property
    def current_tokens(self) -> int:
        """当前 token 数"""
        return self._current_tokens

    @property
    def available_tokens(self) -> int:
        """可用 token 数"""
        return max(0, self.max_tokens - self._current_tokens)

    def to_messages(self) -> List[Dict[str, str]]:
        """
        转换为 API 消息格式

        Returns:
            消息列表
        """
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def save(self, file_path: str) -> None:
        """
        保存上下文到文件

        Args:
            file_path: 文件路径
        """
        data = {
            "max_tokens": self.max_tokens,
            "messages": [m.to_dict() for m in self.messages],
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Context saved to {file_path}")

    def load(self, file_path: str) -> None:
        """
        从文件加载上下文

        Args:
            file_path: 文件路径
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.max_tokens = data.get("max_tokens", 4096)
        self.messages = [
            Message(**msg) for msg in data.get("messages", [])
        ]
        self._current_tokens = sum(m.token_count for m in self.messages)

        logger.info(f"Context loaded from {file_path}")

    def copy(self) -> "ContextManager":
        """
        创建上下文副本

        Returns:
            新的 ContextManager 实例
        """
        new_ctx = ContextManager(max_tokens=self.max_tokens)
        new_ctx.messages = [Message(**m.to_dict()) for m in self.messages]
        new_ctx._current_tokens = self._current_tokens
        return new_ctx
