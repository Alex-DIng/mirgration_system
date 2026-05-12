"""
LLM 客户端实现 - LLM Client Implementation
"""

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """
    LLM 响应

    Attributes:
        text: 生成的文本
        prompt_tokens: 输入 token 数
        completion_tokens: 输出 token 数
        total_tokens: 总 token 数
        finish_reason: 结束原因
    """
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = "stop"


class LLMClient:
    """
    LLM 客户端

    封装对私有 LLM API 的调用，支持重试和错误处理。

    示例:
        client = LLMClient(
            endpoint="http://localhost:8080/v1",
            api_key="your-key",
            model="private-llm"
        )
        response = client.complete("Hello")
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model: str = "private-llm",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        初始化客户端

        Args:
            endpoint: API 端点
            api_key: API 密钥
            model: 模型名称
            max_tokens: 最大输出 token 数
            temperature: 温度参数
            timeout: 请求超时 (秒)
            max_retries: 最大重试次数
            retry_delay: 重试延迟 (秒)
        """
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._session = None

    def _get_session(self):
        """获取 HTTP Session"""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                })
            except ImportError:
                logger.error("requests library not installed")
                raise
        return self._session

    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送补全请求

        Args:
            prompt: 用户提示
            system_message: 系统消息
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """
        发送对话请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
        }

        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self._send_request(payload)
                return self._parse_response(response)
            except Exception as e:
                last_error = e
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))

        logger.error(f"All retries failed: {last_error}")
        raise last_error

    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        session = self._get_session()
        url = f"{self.endpoint}/chat/completions"

        response = session.post(
            url,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _parse_response(self, data: Dict[str, Any]) -> LLMResponse:
        """解析响应"""
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("No choices in response")

        choice = choices[0]
        message = choice.get("message", {})
        text = message.get("content", "")

        usage = data.get("usage", {})

        return LLMResponse(
            text=text,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def complete_stream(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ):
        """
        流式补全

        Args:
            prompt: 用户提示
            system_message: 系统消息
            **kwargs: 其他参数

        Yields:
            文本片段
        """
        # TODO: 实现流式输出
        logger.warning("Streaming not yet implemented")
        yield self.complete(prompt, system_message, **kwargs).text
