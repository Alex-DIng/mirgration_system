"""
C 语言解析器 - C Parser

基于 tree-sitter 实现 C 语言源码解析，提取：
    - 函数定义 (签名、参数、调用关系)
    - 结构体定义
    - 枚举定义
    - 宏定义
    - 全局变量
    - 头文件依赖

输出统一的 IR 格式供后续分析使用。
"""

from .parser import CParser
from .ast_builder import ASTBuilder

__all__ = ["CParser", "ASTBuilder"]
