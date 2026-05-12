"""
数据流分析器实现 - Data Flow Analyzer Implementation
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class DataFlow:
    """
    数据流记录

    描述一个数据对象在程序中的流动路径。

    Attributes:
        data_type: 数据类型 (如 Order, Account)
        start_func: 数据创建的函数
        end_func: 数据销毁的函数
        path: 经过的函数路径
        operations: 在路径上的操作 (read, write, modify)
    """
    data_type: str
    start_func: Optional[str] = None
    end_func: Optional[str] = None
    path: List[str] = field(default_factory=list)
    operations: List[Dict[str, str]] = field(default_factory=list)

    def add_step(self, func_name: str, operation: str = "pass") -> None:
        """
        添加流动步骤

        Args:
            func_name: 函数名
            operation: 操作类型 (read, write, modify, pass)
        """
        self.path.append(func_name)
        self.operations.append({
            "function": func_name,
            "operation": operation,
        })

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "data_type": self.data_type,
            "start": self.start_func,
            "end": self.end_func,
            "path": self.path,
            "operations": self.operations,
        }


class DataFlowAnalyzer:
    """
    数据流分析器

    分析数据对象在函数间的流动路径。

    功能:
        - 追踪指定类型的实例流动
        - 识别数据的读写操作
        - 生成数据流图
    """

    def __init__(self):
        """初始化分析器"""
        self.flows: List[DataFlow] = []
        self._type_usages: Dict[str, List[str]] = {}

    def analyze(
        self,
        ir_functions: List[Any],
        target_types: Optional[List[str]] = None
    ) -> List[DataFlow]:
        """
        执行数据流分析

        Args:
            ir_functions: IR 函数列表
            target_types: 要追踪的数据类型列表

        Returns:
            数据流列表
        """
        logger.info(f"Starting data flow analysis for types: {target_types}")

        self.flows = []
        self._type_usages = {}

        # 第一遍：收集所有类型的使用位置
        for func in ir_functions:
            self._collect_type_usages(func)

        # 第二遍：构建数据流
        if target_types:
            for data_type in target_types:
                self._build_data_flow(data_type, ir_functions)
        else:
            # 分析所有结构体类型
            for data_type in self._type_usages.keys():
                self._build_data_flow(data_type, ir_functions)

        logger.info(f"Found {len(self.flows)} data flows")
        return self.flows

    def _collect_type_usages(self, func: Any) -> None:
        """
        收集函数中的类型使用

        Args:
            func: IRFunction 对象
        """
        # 从参数类型收集
        for param in getattr(func, 'parameters', []):
            param_type = self._normalize_type(param.type)
            if param_type not in self._type_usages:
                self._type_usages[param_type] = []
            self._type_usages[param_type].append(func.name)

        # 从返回类型收集
        return_type = getattr(func, 'return_type', None)
        if return_type:
            normalized = self._normalize_type(return_type)
            if normalized not in self._type_usages:
                self._type_usages[normalized] = []
            self._type_usages[normalized].append(func.name)

    def _normalize_type(self, type_str: str) -> str:
        """
        标准化类型字符串

        Args:
            type_str: 类型字符串 (如 "Order*", "struct Order")

        Returns:
            标准化后的类型名
        """
        # 移除指针、const 等修饰符
        type_str = type_str.replace("*", "").replace("const", "").strip()
        # 移除 struct 前缀
        type_str = type_str.replace("struct ", "").strip()
        return type_str

    def _build_data_flow(
        self,
        data_type: str,
        ir_functions: List[Any]
    ) -> None:
        """
        构建特定类型的数据流

        Args:
            data_type: 数据类型
            ir_functions: IR 函数列表
        """
        if data_type not in self._type_usages:
            return

        usage_funcs = self._type_usages[data_type]
        logger.debug(f"Building data flow for {data_type}, used in: {usage_funcs}")

        flow = DataFlow(data_type=data_type)

        # 查找创建点 (返回该类型的函数)
        for func in ir_functions:
            if self._normalize_type(getattr(func, 'return_type', '')) == data_type:
                flow.start_func = func.name
                flow.add_step(func.name, "create")
                break

        # 构建调用路径
        for func_name in usage_funcs:
            flow.add_step(func_name, "use")

        # 查找销毁点 (通常是释放内存的函数)
        # TODO: 实现更复杂的销毁点检测

        if flow.path:
            self.flows.append(flow)

    def get_flows_for_type(self, data_type: str) -> List[DataFlow]:
        """
        获取指定类型的所有数据流

        Args:
            data_type: 数据类型

        Returns:
            数据流列表
        """
        return [f for f in self.flows if f.data_type == data_type]

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            包含所有数据流的字典
        """
        return {
            "flows": [f.to_dict() for f in self.flows],
            "type_usages": self._type_usages,
        }
