"""
依赖分析器实现 - Dependency Analyzer Implementation
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DependencyEdge:
    """
    依赖边

    Attributes:
        source: 依赖方
        target: 被依赖方
        dependency_type: 依赖类型 (include, call, global_var)
        strength: 依赖强度 (1-10)
    """
    source: str
    target: str
    dependency_type: str = "call"
    strength: int = 5


@dataclass
class DependencyGraph:
    """
    依赖图

    存储文件/模块间的依赖关系。

    Attributes:
        nodes: 节点集合 (文件或模块)
        edges: 依赖边集合
        adjacency: 邻接表
    """
    nodes: Set[str] = field(default_factory=set)
    edges: List[DependencyEdge] = field(default_factory=list)
    adjacency: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))

    def add_node(self, node: str) -> None:
        """添加节点"""
        self.nodes.add(node)

    def add_edge(self, edge: DependencyEdge) -> None:
        """添加依赖边"""
        self.edges.append(edge)
        self.adjacency[edge.source].append(edge.target)

    def get_dependencies(self, node: str) -> List[str]:
        """获取节点的所有依赖"""
        return self.adjacency.get(node, [])

    def get_dependents(self, node: str) -> List[str]:
        """获取所有依赖该节点的节点"""
        return [
            source for source, edges in self.adjacency.items()
            if node in edges
        ]

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "nodes": list(self.nodes),
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.dependency_type,
                    "strength": e.strength,
                }
                for e in self.edges
            ],
        }


class DependencyAnalyzer:
    """
    依赖分析器

    分析文件间的依赖关系，确定迁移顺序。

    原则:
        - 被依赖少的文件优先迁移
        - 相互依赖的文件放在同一批次
        - 核心工具函数优先迁移
    """

    def __init__(self):
        """初始化分析器"""
        self.graph = DependencyGraph()
        self._file_functions: Dict[str, List[str]] = {}
        self._function_files: Dict[str, str] = {}

    def analyze(
        self,
        ir_functions: List[Any],
        files: Optional[List[str]] = None
    ) -> DependencyGraph:
        """
        执行依赖分析

        Args:
            ir_functions: IR 函数列表
            files: 文件列表

        Returns:
            依赖图
        """
        logger.info("Starting dependency analysis...")

        self.graph = DependencyGraph()
        self._file_functions = {}
        self._function_files = {}

        # 构建函数到文件的映射
        for func in ir_functions:
            file_path = getattr(func, 'file_path', '<unknown>')
            func_name = getattr(func, 'name', '<anonymous>')

            if file_path not in self._file_functions:
                self._file_functions[file_path] = []
            self._file_functions[file_path].append(func_name)
            self._function_files[func_name] = file_path

            self.graph.add_node(file_path)

        # 添加显式指定的文件
        if files:
            for f in files:
                self.graph.add_node(f)

        # 分析调用依赖
        self._analyze_call_dependencies(ir_functions)

        # 分析包含依赖
        self._analyze_include_dependencies()

        logger.info(f"Dependency graph: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
        return self.graph

    def _analyze_call_dependencies(self, ir_functions: List[Any]) -> None:
        """
        分析函数调用产生的文件依赖

        Args:
            ir_functions: IR 函数列表
        """
        for func in ir_functions:
            caller_file = getattr(func, 'file_path', None)
            if not caller_file:
                continue

            calls = getattr(func, 'calls', [])
            for call in calls:
                callee_name = getattr(call, 'name', None)
                if callee_name and callee_name in self._function_files:
                    callee_file = self._function_files[callee_name]
                    if callee_file != caller_file:
                        # 外部调用，产生文件依赖
                        edge = DependencyEdge(
                            source=caller_file,
                            target=callee_file,
                            dependency_type="call",
                            strength=7,  # 调用依赖较强
                        )
                        self.graph.add_edge(edge)

    def _analyze_include_dependencies(self) -> None:
        """
        分析 #include 产生的依赖

        TODO: 需要解析头文件内容
        """
        # 这里需要实际的 #include 解析
        # 暂时跳过
        pass

    def get_migration_order(self) -> List[List[str]]:
        """
        获取推荐的迁移顺序

        使用拓扑排序确定迁移批次。

        Returns:
            批次列表，每批是可以并行迁移的文件
        """
        if not self.graph.nodes:
            return []

        # 计算每个节点的入度 (被依赖数)
        in_degree = {node: 0 for node in self.graph.nodes}
        for edge in self.graph.edges:
            if edge.target in in_degree:
                in_degree[edge.target] += 1

        # Kahn 算法进行拓扑排序
        batches = []
        remaining = set(self.graph.nodes)

        while remaining:
            # 找出入度为 0 的节点 (没有未处理的依赖)
            batch = [
                node for node in remaining
                if in_degree.get(node, 0) == 0
            ]

            if not batch:
                # 存在循环依赖，取剩余节点中入度最小的
                min_degree = min(in_degree.get(n, 0) for n in remaining)
                batch = [
                    node for node in remaining
                    if in_degree.get(node, 0) == min_degree
                ]
                logger.warning(f"Circular dependency detected, batch: {batch}")

            batches.append(batch)

            # 更新入度
            for node in batch:
                remaining.remove(node)
                for dependent in self.graph.get_dependents(node):
                    if dependent in in_degree:
                        in_degree[dependent] -= 1

        return batches

    def get_critical_files(self, top_n: int = 5) -> List[str]:
        """
        获取最关键的文件 (被依赖最多的文件)

        Args:
            top_n: 返回的文件数量

        Returns:
            关键文件列表
        """
        dependency_count = defaultdict(int)
        for edge in self.graph.edges:
            dependency_count[edge.target] += 1

        sorted_files = sorted(
            dependency_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [f for f, _ in sorted_files[:top_n]]

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            包含依赖图和迁移顺序的字典
        """
        return {
            "graph": self.graph.to_dict(),
            "migration_order": self.get_migration_order(),
            "critical_files": self.get_critical_files(),
        }
