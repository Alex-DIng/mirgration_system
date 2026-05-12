"""
解析器模块 - Parser Module

负责将 C 语言源码解析为中间表示 (IR)：
    - c_parser: C 语言解析器 (基于 tree-sitter)
    - ir: 中间表示定义

使用示例:
    from src.parser.c_parser import CParser

    parser = CParser()
    result = parser.parse_file("source.c")

    # 获取函数列表
    for func in result.functions:
        print(f"Function: {func.name}")
"""

from . import ir
from . import c_parser

__all__ = ["ir", "c_parser"]
