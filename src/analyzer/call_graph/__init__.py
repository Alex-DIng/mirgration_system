"""
调用图分析模块 - Call Graph Analysis

构建 C 语言函数的调用关系图，识别：
- 函数调用链（call chains）
- 递归调用（direct/indirect recursion）
- 间接调用（通过函数指针）
- 调用深度与复杂度统计

输出结果供 LLM 翻译阶段理解函数间的调用关系，
确保生成的 Java 代码保持正确的调用依赖。
"""

from .call_graph import CallGraph, CallNode, CallEdge
from .analyzer import CallGraphAnalyzer

__all__ = [
    "CallGraph",
    "CallNode",
    "CallEdge",
    "CallGraphAnalyzer",
]