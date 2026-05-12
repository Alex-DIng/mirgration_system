"""
调用图数据结构 - Call Graph Data Structures

定义调用图的核心数据类：
- CallNode: 函数节点
- CallEdge: 调用边
- CallGraph: 完整的调用图
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from collections import defaultdict


@dataclass
class CallNode:
    """
    调用图节点 - 代表一个函数

    Attributes:
        name: 函数名
        file_path: 源文件路径
        line_number: 函数定义行号
        is_entry_point: 是否为入口函数（如 main）
        is_recursive: 是否存在递归调用
        callers: 调用此函数的函数名集合
        callees: 此函数调用的其他函数名集合
    """
    name: str
    file_path: str
    line_number: int
    is_entry_point: bool = False
    is_recursive: bool = False
    callers: Set[str] = field(default_factory=set)
    callees: Set[str] = field(default_factory=set)

    def add_caller(self, caller: str) -> None:
        """添加调用者"""
        self.callers.add(caller)

    def add_callee(self, callee: str) -> None:
        """添加被调用者"""
        self.callees.add(callee)


@dataclass
class CallEdge:
    """
    调用边 - 代表一次函数调用关系

    Attributes:
        caller: 调用方函数名
        callee: 被调用方函数名
        call_site: 调用位置的行号
        call_type: 调用类型 (direct/indirect/recursive)
        is_recursive: 是否为递归调用
    """
    caller: str
    callee: str
    call_site: int
    call_type: str = "direct"  # direct, indirect, recursive
    is_recursive: bool = False

    def __post_init__(self) -> None:
        if self.call_type == "recursive":
            self.is_recursive = True


class CallGraph:
    """
    调用图 - 存储和分析函数调用关系

    使用邻接表存储，支持：
    - 添加节点和边
    - 查询调用者/被调用者
    - 检测递归
    - 计算调用链
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, CallNode] = {}
        self.edges: List[CallEdge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def add_node(self, node: CallNode) -> None:
        """添加函数节点"""
        self.nodes[node.name] = node

    def add_edge(self, edge: CallEdge) -> None:
        """添加调用边"""
        self.edges.append(edge)
        self.adjacency[edge.caller].append(edge.callee)
        self.reverse_adjacency[edge.callee].append(edge.caller)

        # 更新节点的调用关系
        if edge.caller in self.nodes:
            self.nodes[edge.caller].add_callee(edge.callee)
        if edge.callee in self.nodes:
            self.nodes[edge.callee].add_caller(edge.caller)

    def get_callers(self, func_name: str) -> List[str]:
        """获取调用指定函数的所有函数"""
        return self.reverse_adjacency.get(func_name, [])

    def get_callees(self, func_name: str) -> List[str]:
        """获取指定函数调用的所有函数"""
        return self.adjacency.get(func_name, [])

    def find_recursive_functions(self) -> Set[str]:
        """
        查找所有递归函数（包括直接递归和间接递归）

        Returns:
            递归函数名集合
        """
        recursive_funcs = set()

        for func_name in self.nodes:
            if self._has_path_to_self(func_name, visited=set()):
                recursive_funcs.add(func_name)
                self.nodes[func_name].is_recursive = True

        return recursive_funcs

    def _has_path_to_self(self, start: str, visited: Set[str]) -> bool:
        """检查从 start 出发是否存在回到 start 的路径"""
        if start in visited:
            return start == start  # 第一次访问不算

        visited.add(start)

        for callee in self.adjacency.get(start, []):
            if callee == start:
                return True
            if callee in self.nodes and self._has_path_to_self(callee, visited.copy()):
                return True

        return False

    def get_call_chain(self, from_func: str, to_func: str) -> List[List[str]]:
        """
        查找从 from_func 到 to_func 的所有调用路径

        Returns:
            所有可能的调用路径列表
        """
        chains = []
        self._dfs_chain(from_func, to_func, [from_func], set(), chains)
        return chains

    def _dfs_chain(
        self,
        current: str,
        target: str,
        path: List[str],
        visited: Set[str],
        chains: List[List[str]]
    ) -> None:
        """DFS 查找调用路径"""
        if current == target:
            chains.append(path.copy())
            return

        if current in visited:
            return

        visited.add(current)

        for callee in self.adjacency.get(current, []):
            path.append(callee)
            self._dfs_chain(callee, target, path, visited, chains)
            path.pop()

        visited.remove(current)

    def get_entry_points(self) -> List[CallNode]:
        """获取所有入口函数（没有调用者的函数）"""
        return [
            node for node in self.nodes.values()
            if not self.reverse_adjacency.get(node.name)
        ]

    def get_leaf_functions(self) -> List[CallNode]:
        """获取所有叶子函数（不调用其他函数的函数）"""
        return [
            node for node in self.nodes.values()
            if not self.adjacency.get(node.name)
        ]

    def compute_call_depth(self, func_name: str) -> int:
        """
        计算函数的最大调用深度

        Args:
            func_name: 函数名

        Returns:
            最大调用深度
        """
        if func_name not in self.nodes:
            return 0

        return self._compute_depth(func_name, {})

    def _compute_depth(self, func_name: str, memo: Dict[str, int]) -> int:
        """递归计算调用深度（带记忆化）"""
        if func_name in memo:
            return memo[func_name]

        callees = self.adjacency.get(func_name, [])
        if not callees:
            memo[func_name] = 1
            return 1

        # 检测循环依赖，避免无限递归
        memo[func_name] = 1  # 临时标记

        max_depth = 0
        for callee in callees:
            if callee != func_name:  # 跳过自递归
                depth = self._compute_depth(callee, memo)
                max_depth = max(max_depth, depth)

        memo[func_name] = max_depth + 1
        return memo[func_name]

    def to_dict(self) -> dict:
        """将调用图转换为字典格式，便于序列化"""
        return {
            "nodes": [
                {
                    "name": node.name,
                    "file_path": node.file_path,
                    "line_number": node.line_number,
                    "is_entry_point": node.is_entry_point,
                    "is_recursive": node.is_recursive,
                    "callers": list(node.callers),
                    "callees": list(node.callees),
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "caller": edge.caller,
                    "callee": edge.callee,
                    "call_site": edge.call_site,
                    "call_type": edge.call_type,
                    "is_recursive": edge.is_recursive,
                }
                for edge in self.edges
            ],
        }
