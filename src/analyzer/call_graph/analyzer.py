"""
调用图分析器 - Call Graph Analyzer

从 IR 中提取函数调用关系，构建调用图并进行分析。
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .call_graph import CallGraph, CallNode, CallEdge


class CallGraphAnalyzer:
    """
    调用图分析器

    负责：
    1. 从 IR 函数定义中提取调用关系
    2. 构建完整的调用图
    3. 分析调用模式（递归、间接调用等）
    4. 生成分析报告供 LLM 翻译使用
    """

    def __init__(self) -> None:
        self.graph = CallGraph()
        self._function_map: Dict[str, CallNode] = {}

    def add_function(self, name: str, file_path: str, line_number: int) -> CallNode:
        """添加函数节点到图中"""
        node = CallNode(
            name=name,
            file_path=file_path,
            line_number=line_number,
        )
        self.graph.add_node(node)
        self._function_map[name] = node
        return node

    def add_call(
        self,
        caller: str,
        callee: str,
        call_site: int,
        call_type: str = "direct"
    ) -> CallEdge:
        """
        添加函数调用关系

        Args:
            caller: 调用方函数名
            callee: 被调用方函数名
            call_site: 调用位置的行号
            call_type: 调用类型 (direct/indirect/recursive)
        """
        # 确定是否为递归调用
        is_recursive = caller == callee or call_type == "recursive"
        if is_recursive:
            call_type = "recursive"

        edge = CallEdge(
            caller=caller,
            callee=callee,
            call_site=call_site,
            call_type=call_type,
            is_recursive=is_recursive,
        )
        self.graph.add_edge(edge)
        return edge

    def build_from_ir(self, ir_functions: List[Dict[str, Any]]) -> CallGraph:
        """
        从 IR 函数列表构建调用图

        Args:
            ir_functions: IR 函数列表，每个函数包含：
                - name: 函数名
                - file_path: 文件路径
                - line_number: 定义行号
                - calls: 调用的函数列表 [{name, line}]

        Returns:
            构建完成的调用图
        """
        # 第一遍：添加所有函数节点
        for func in ir_functions:
            self.add_function(
                name=func["name"],
                file_path=func.get("file_path", "unknown"),
                line_number=func.get("line_number", 0),
            )

        # 第二遍：添加调用边
        for func in ir_functions:
            caller_name = func["name"]
            calls = func.get("calls", [])

            for call in calls:
                callee_name = call.get("name")
                if callee_name:
                    call_type = call.get("type", "direct")
                    call_site = call.get("line", 0)
                    self.add_call(
                        caller=caller_name,
                        callee=callee_name,
                        call_site=call_site,
                        call_type=call_type,
                    )

        # 检测递归函数
        self.graph.find_recursive_functions()

        # 标记入口函数
        self._mark_entry_points()

        return self.graph

    def _mark_entry_points(self) -> None:
        """标记常见的入口函数"""
        entry_point_names = ["main", "WinMain", "mainCRTStartup"]

        for name in entry_point_names:
            if name in self.graph.nodes:
                self.graph.nodes[name].is_entry_point = True

        # 如果没有找到标准入口，将没有被调用的函数视为潜在入口
        if not any(n.is_entry_point for n in self.graph.nodes.values()):
            for node in self.graph.get_entry_points():
                node.is_entry_point = True

    def analyze(self) -> Dict[str, Any]:
        """
        执行完整的调用图分析

        Returns:
            分析报告字典
        """
        recursive_funcs = self.graph.find_recursive_functions()

        return {
            "total_functions": len(self.graph.nodes),
            "total_calls": len(self.graph.edges),
            "entry_points": [n.name for n in self.graph.get_entry_points()],
            "leaf_functions": [n.name for n in self.graph.get_leaf_functions()],
            "recursive_functions": list(recursive_funcs),
            "indirect_calls": [
                {
                    "caller": e.caller,
                    "callee": e.callee,
                    "line": e.call_site,
                }
                for e in self.graph.edges
                if e.call_type == "indirect"
            ],
            "max_call_depth": self._get_max_call_depth(),
            "average_calls_per_function": (
                len(self.graph.edges) / len(self.graph.nodes)
                if self.graph.nodes else 0
            ),
        }

    def _get_max_call_depth(self) -> int:
        """获取整个调用图的最大调用深度"""
        if not self.graph.nodes:
            return 0

        return max(
            self.graph.compute_call_depth(name)
            for name in self.graph.nodes
        )

    def get_call_report(self, func_name: str) -> Optional[Dict[str, Any]]:
        """
        生成单个函数的调用报告

        Args:
            func_name: 函数名

        Returns:
            函数调用报告
        """
        if func_name not in self.graph.nodes:
            return None

        node = self.graph.nodes[func_name]

        return {
            "function": func_name,
            "file": node.file_path,
            "line": node.line_number,
            "is_recursive": node.is_recursive,
            "is_entry_point": node.is_entry_point,
            "callers": list(node.callers),
            "callees": list(node.callees),
            "call_depth": self.graph.compute_call_depth(func_name),
            "call_chains": [
                chain for target in node.callers
                for chain in self.graph.get_call_chain(target, func_name)
            ][:10],  # 限制数量避免报告过大
        }

    def export_to_json(self, output_path: str) -> None:
        """
        将调用图导出为 JSON 文件

        Args:
            output_path: 输出文件路径
        """
        import json

        data = {
            "analysis": self.analyze(),
            "graph": self.graph.to_dict(),
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
