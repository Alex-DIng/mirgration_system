"""
数据流分析模块 - Data Flow Analysis

追踪关键数据 (订单、行情、持仓等) 在各函数间的流动路径，
识别数据的创建、修改、销毁位置。

主要功能:
    - 追踪结构体实例的生命周期
    - 识别关键数据的传递路径
    - 检测数据竞争和副作用

使用示例:
    analyzer = DataFlowAnalyzer()
    flows = analyzer.analyze(ir_functions, target_struct="Order")
"""

from .analyzer import DataFlowAnalyzer, DataFlow

__all__ = ["DataFlowAnalyzer", "DataFlow"]
