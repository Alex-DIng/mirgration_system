"""
字符串工具 - String Utilities

提供命名转换等字符串处理功能。
"""

import re


def to_camel_case(name: str) -> str:
    """
    转换为驼峰命名 (camelCase)

    Args:
        name: 原始名称 (蛇形命名或空格分隔)

    Returns:
        驼峰命名

    Example:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("Hello World")
        'helloWorld'
    """
    # 先转换为小写，按非字母数字分割
    words = re.split(r'[^a-zA-Z0-9]', name.lower())
    # 首词小写，后续词首字母大写
    return words[0] + ''.join(word.capitalize() for word in words[1:])


def to_pascal_case(name: str) -> str:
    """
    转换为帕斯卡命名 (PascalCase / UpperCamelCase)

    Args:
        name: 原始名称

    Returns:
        帕斯卡命名

    Example:
        >>> to_pascal_case("hello_world")
        'HelloWorld'
        >>> to_pascal_case("hello world")
        'HelloWorld'
    """
    words = re.split(r'[^a-zA-Z0-9]', name)
    return ''.join(word.capitalize() for word in words)


def to_snake_case(name: str) -> str:
    """
    转换为蛇形命名 (snake_case)

    Args:
        name: 原始名称 (驼峰命名或帕斯卡命名)

    Returns:
        蛇形命名

    Example:
        >>> to_snake_case("helloWorld")
        'hello_world'
        >>> to_snake_case("HelloWorld")
        'hello_world'
    """
    # 在大写字母前插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def to_constant_case(name: str) -> str:
    """
    转换为常量命名 (SCREAMING_SNAKE_CASE)

    Args:
        name: 原始名称

    Returns:
        常量命名

    Example:
        >>> to_constant_case("helloWorld")
        'HELLO_WORLD'
    """
    snake = to_snake_case(name)
    return snake.upper()


def to_kebab_case(name: str) -> str:
    """
    转换为烤串命名 (kebab-case)

    Args:
        name: 原始名称

    Returns:
        烤串命名

    Example:
        >>> to_kebab_case("helloWorld")
        'hello-world'
    """
    snake = to_snake_case(name)
    return snake.replace('_', '-')


def remove_prefix(s: str, prefix: str) -> str:
    """移除前缀"""
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def remove_suffix(s: str, suffix: str) -> str:
    """移除后缀"""
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
