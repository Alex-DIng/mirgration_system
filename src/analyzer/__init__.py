"""
静态分析模块 - Static Analyzer

对 IR 进行多维度静态分析，提取 LLM 翻译所需的结构化信息：
    - call_graph: 调用图分析 (函数调用关系、递归检测)
    - data_flow: 数据流分析 (关键数据流动路径)
    - dependency: 依赖分析 (文件间依赖、迁移顺序)

使用示例:
    from src.analyzer.call_graph import CallGraphAnalyzer
    from src.analyzer.data_flow import DataFlowAnalyzer

    # 调用图分析
    call_analyzer = CallGraphAnalyzer()
    graph = call_analyzer.build_from_ir(functions)
"""

from . import call_graph
from . import data_flow
from . import dependency

__all__ = ["call_graph", "data_flow", "dependency"]
