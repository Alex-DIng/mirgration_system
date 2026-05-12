"""
Token 计数工具 - Token Utilities

估算文本的 token 数量，用于 LLM 上下文管理。
"""


def count_tokens(text: str, method: str = "simple") -> int:
    """
    估算文本的 token 数量

    Args:
        text: 文本内容
        method: 计数方法
            - simple: 简单估算 (每 4 字符 1 token)
            - char: 按字符数 (每 4 字符 1 token)
            - word: 按单词数 (英文适用)

    Returns:
        估算的 token 数
    """
    if not text:
        return 0

    if method == "simple" or method == "char":
        # 简单估算：每 4 个字符约 1 个 token
        return len(text) // 4 + 1

    elif method == "word":
        # 按单词计数 (英文适用)
        import re
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    else:
        # 默认简单估算
        return len(text) // 4 + 1


def estimate_prompt_cost(
    prompt_text: str,
    response_text: str,
    price_per_1k_tokens: float = 0.001
) -> float:
    """
    估算 API 调用成本

    Args:
        prompt_text: 提示词文本
        response_text: 响应文本
        price_per_1k_tokens: 每 1000 token 的价格

    Returns:
        估算成本 (美元)
    """
    prompt_tokens = count_tokens(prompt_text)
    response_tokens = count_tokens(response_text)
    total_tokens = prompt_tokens + response_tokens

    return (total_tokens / 1000) * price_per_1k_tokens


def check_token_limit(
    prompt_text: str,
    max_tokens: int = 4096,
    reserved_tokens: int = 100
) -> bool:
    """
    检查是否超出 token 限制

    Args:
        prompt_text: 提示词文本
        max_tokens: 最大 token 数
        reserved_tokens: 预留 token 数 (用于响应)

    Returns:
        是否在限制内
    """
    available = max_tokens - reserved_tokens
    return count_tokens(prompt_text) <= available
