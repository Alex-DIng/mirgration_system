"""
调用图分析器单元测试 - Call Graph Analyzer Unit Tests

测试覆盖：
- CallNode: 函数节点创建和调用关系添加
- CallEdge: 调用边的创建和类型判断
- CallGraph: 调用图的构建、查询、递归检测
- CallGraphAnalyzer: IR 到调用图的转换和分析报告
"""

import pytest
from pathlib import Path

# 导入被测试模块
from src.analyzer.call_graph import CallGraph, CallNode, CallEdge, CallGraphAnalyzer


# =============================================================================
# CallNode 测试
# =============================================================================

class TestCallNode:
    """CallNode 数据类测试"""

    def test_create_node(self):
        """测试创建基本函数节点"""
        node = CallNode(
            name="test_func",
            file_path="test.c",
            line_number=10
        )

        assert node.name == "test_func"
        assert node.file_path == "test.c"
        assert node.line_number == 10
        assert node.is_entry_point is False
        assert node.is_recursive is False
        assert len(node.callers) == 0
        assert len(node.callees) == 0

    def test_node_with_entry_point(self):
        """测试入口函数节点"""
        node = CallNode(
            name="main",
            file_path="main.c",
            line_number=1,
            is_entry_point=True
        )

        assert node.is_entry_point is True

    def test_add_caller(self):
        """测试添加调用者"""
        node = CallNode(name="callee", file_path="test.c", line_number=10)
        node.add_caller("caller1")
        node.add_caller("caller2")

        assert "caller1" in node.callers
        assert "caller2" in node.callers
        assert len(node.callers) == 2

    def test_add_callee(self):
        """测试添加被调用者"""
        node = CallNode(name="caller", file_path="test.c", line_number=10)
        node.add_callee("func_a")
        node.add_callee("func_b")

        assert "func_a" in node.callees
        assert "func_b" in node.callees
        assert len(node.callees) == 2

    def test_duplicate_caller_not_added(self):
        """测试重复的调用者不会重复添加"""
        node = CallNode(name="callee", file_path="test.c", line_number=10)
        node.add_caller("caller1")
        node.add_caller("caller1")

        assert len(node.callers) == 1


# =============================================================================
# CallEdge 测试
# =============================================================================

class TestCallEdge:
    """CallEdge 数据类测试"""

    def test_create_direct_edge(self):
        """测试创建直接调用边"""
        edge = CallEdge(
            caller="main",
            callee="helper",
            call_site=15
        )

        assert edge.caller == "main"
        assert edge.callee == "helper"
        assert edge.call_site == 15
        assert edge.call_type == "direct"
        assert edge.is_recursive is False

    def test_create_recursive_edge(self):
        """测试创建递归调用边"""
        edge = CallEdge(
            caller="factorial",
            callee="factorial",
            call_site=10,
            call_type="recursive"
        )

        assert edge.call_type == "recursive"
        assert edge.is_recursive is True

    def test_recursive_flag_from_type(self):
        """测试 call_type 自动设置 is_recursive"""
        edge = CallEdge(
            caller="func",
            callee="func",
            call_site=5,
            call_type="recursive"
        )

        assert edge.is_recursive is True


# =============================================================================
# CallGraph 测试
# =============================================================================

class TestCallGraph:
    """CallGraph 类测试"""

    def test_create_empty_graph(self):
        """测试创建空图"""
        graph = CallGraph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_add_node(self):
        """测试添加节点"""
        graph = CallGraph()
        node = CallNode(name="func1", file_path="test.c", line_number=1)
        graph.add_node(node)

        assert "func1" in graph.nodes
        assert len(graph.nodes) == 1

    def test_add_edge(self):
        """测试添加调用边"""
        graph = CallGraph()

        # 先添加节点
        graph.add_node(CallNode(name="caller", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="callee", file_path="test.c", line_number=10))

        # 添加边
        edge = CallEdge(caller="caller", callee="callee", call_site=5)
        graph.add_edge(edge)

        assert len(graph.edges) == 1
        assert "callee" in graph.adjacency["caller"]
        assert "caller" in graph.reverse_adjacency["callee"]

    def test_add_edge_updates_node_relations(self):
        """测试添加边后节点的 callers/callees 更新"""
        graph = CallGraph()
        graph.add_node(CallNode(name="caller", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="callee", file_path="test.c", line_number=10))

        edge = CallEdge(caller="caller", callee="callee", call_site=5)
        graph.add_edge(edge)

        assert "callee" in graph.nodes["caller"].callees
        assert "caller" in graph.nodes["callee"].callers

    def test_get_callers(self):
        """测试获取调用者列表"""
        graph = CallGraph()
        graph.add_node(CallNode(name="callee", file_path="test.c", line_number=10))
        graph.add_node(CallNode(name="caller1", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="caller2", file_path="test.c", line_number=5))

        graph.add_edge(CallEdge(caller="caller1", callee="callee", call_site=2))
        graph.add_edge(CallEdge(caller="caller2", callee="callee", call_site=6))

        callers = graph.get_callers("callee")

        assert "caller1" in callers
        assert "caller2" in callers
        assert len(callers) == 2

    def test_get_callees(self):
        """测试获取被调用者列表"""
        graph = CallGraph()
        graph.add_node(CallNode(name="caller", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="callee1", file_path="test.c", line_number=10))
        graph.add_node(CallNode(name="callee2", file_path="test.c", line_number=20))

        graph.add_edge(CallEdge(caller="caller", callee="callee1", call_site=5))
        graph.add_edge(CallEdge(caller="caller", callee="callee2", call_site=15))

        callees = graph.get_callees("caller")

        assert "callee1" in callees
        assert "callee2" in callees
        assert len(callees) == 2

    def test_find_direct_recursion(self):
        """测试检测直接递归"""
        graph = CallGraph()
        graph.add_node(CallNode(name="factorial", file_path="test.c", line_number=1))

        # 自己调用自己
        graph.add_edge(CallEdge(
            caller="factorial",
            callee="factorial",
            call_site=5,
            call_type="recursive"
        ))

        recursive_funcs = graph.find_recursive_functions()

        assert "factorial" in recursive_funcs
        assert graph.nodes["factorial"].is_recursive is True

    def test_find_indirect_recursion(self):
        """测试检测间接递归（A -> B -> A）"""
        graph = CallGraph()
        graph.add_node(CallNode(name="func_a", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="func_b", file_path="test.c", line_number=10))

        graph.add_edge(CallEdge(caller="func_a", callee="func_b", call_site=5))
        graph.add_edge(CallEdge(caller="func_b", callee="func_a", call_site=15))

        recursive_funcs = graph.find_recursive_functions()

        assert "func_a" in recursive_funcs
        assert "func_b" in recursive_funcs

    def test_no_recursion(self):
        """测试没有递归的情况"""
        graph = CallGraph()
        graph.add_node(CallNode(name="main", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="helper", file_path="test.c", line_number=10))

        graph.add_edge(CallEdge(caller="main", callee="helper", call_site=5))

        recursive_funcs = graph.find_recursive_functions()

        assert len(recursive_funcs) == 0

    def test_get_call_chain(self):
        """测试获取调用链"""
        graph = CallGraph()

        # 构建调用链：main -> process -> validate -> execute
        for name in ["main", "process", "validate", "execute"]:
            graph.add_node(CallNode(name=name, file_path="test.c", line_number=1))

        graph.add_edge(CallEdge(caller="main", callee="process", call_site=2))
        graph.add_edge(CallEdge(caller="process", callee="validate", call_site=5))
        graph.add_edge(CallEdge(caller="process", callee="execute", call_site=8))

        chains = graph.get_call_chain("main", "validate")

        assert len(chains) > 0
        assert ["main", "process", "validate"] in chains

    def test_get_entry_points(self):
        """测试获取入口函数（没有调用者的函数）"""
        graph = CallGraph()
        graph.add_node(CallNode(name="main", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="helper", file_path="test.c", line_number=10))

        graph.add_edge(CallEdge(caller="main", callee="helper", call_site=5))

        entry_points = graph.get_entry_points()

        assert len(entry_points) == 1
        assert entry_points[0].name == "main"

    def test_get_leaf_functions(self):
        """测试获取叶子函数（不调用其他函数的函数）"""
        graph = CallGraph()
        graph.add_node(CallNode(name="main", file_path="test.c", line_number=1))
        graph.add_node(CallNode(name="pure_func", file_path="test.c", line_number=10))

        graph.add_edge(CallEdge(caller="main", callee="pure_func", call_site=5))

        leaf_funcs = graph.get_leaf_functions()

        assert len(leaf_funcs) == 1
        assert leaf_funcs[0].name == "pure_func"

    def test_compute_call_depth(self):
        """测试计算调用深度"""
        graph = CallGraph()

        # 构建三层调用：main -> level1 -> level2 -> level3
        for name in ["main", "level1", "level2", "level3"]:
            graph.add_node(CallNode(name=name, file_path="test.c", line_number=1))

        graph.add_edge(CallEdge(caller="main", callee="level1", call_site=1))
        graph.add_edge(CallEdge(caller="level1", callee="level2", call_site=1))
        graph.add_edge(CallEdge(caller="level2", callee="level3", call_site=1))

        depth = graph.compute_call_depth("main")

        assert depth == 4  # main -> level1 -> level2 -> level3

    def test_to_dict(self):
        """测试序列化为字典"""
        graph = CallGraph()
        graph.add_node(CallNode(name="func", file_path="test.c", line_number=1))

        result = graph.to_dict()

        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 1


# =============================================================================
# CallGraphAnalyzer 测试
# =============================================================================

class TestCallGraphAnalyzer:
    """CallGraphAnalyzer 类测试"""

    def test_add_function(self):
        """测试添加函数"""
        analyzer = CallGraphAnalyzer()
        node = analyzer.add_function("test_func", "test.c", 10)

        assert node.name == "test_func"
        assert "test_func" in analyzer._function_map

    def test_add_call(self):
        """测试添加调用关系"""
        analyzer = CallGraphAnalyzer()
        analyzer.add_function("caller", "test.c", 1)
        analyzer.add_function("callee", "test.c", 10)

        edge = analyzer.add_call("caller", "callee", 5)

        assert edge.caller == "caller"
        assert edge.callee == "callee"
        assert len(analyzer.graph.edges) == 1

    def test_build_from_ir(self, sample_ir_with_calls):
        """测试从 IR 构建调用图"""
        analyzer = CallGraphAnalyzer()
        graph = analyzer.build_from_ir(sample_ir_with_calls)

        # 验证节点数量
        assert len(graph.nodes) == 4

        # 验证调用关系
        assert "log_message" in graph.get_callees("process_order")
        assert "validate_order" in graph.get_callees("process_order")
        assert "execute_order" in graph.get_callees("process_order")

    def test_build_from_ir_marks_entry_points(self):
        """测试从 IR 构建时标记入口函数"""
        analyzer = CallGraphAnalyzer()
        ir_functions = [
            {
                "name": "main",
                "file_path": "main.c",
                "line_number": 1,
                "calls": [{"name": "helper", "line": 5, "type": "direct"}]
            },
            {
                "name": "helper",
                "file_path": "helper.c",
                "line_number": 10,
                "calls": []
            }
        ]

        analyzer.build_from_ir(ir_functions)

        assert analyzer.graph.nodes["main"].is_entry_point is True

    def test_analyze(self, sample_ir_with_calls):
        """测试完整分析报告"""
        analyzer = CallGraphAnalyzer()
        analyzer.build_from_ir(sample_ir_with_calls)

        report = analyzer.analyze()

        assert report["total_functions"] == 4
        assert report["total_calls"] == 5
        assert "process_order" in report["entry_points"]
        assert "validate_order" in report["leaf_functions"]

    def test_get_call_report(self, sample_ir_with_calls):
        """测试获取单个函数的调用报告"""
        analyzer = CallGraphAnalyzer()
        analyzer.build_from_ir(sample_ir_with_calls)

        report = analyzer.get_call_report("process_order")

        assert report is not None
        assert report["function"] == "process_order"
        assert "log_message" in report["callees"]

    def test_get_call_report_not_found(self):
        """测试获取不存在的函数报告"""
        analyzer = CallGraphAnalyzer()

        report = analyzer.get_call_report("nonexistent")

        assert report is None

    def test_export_to_json(self, sample_ir_with_calls, temp_output_dir):
        """测试导出 JSON 文件"""
        analyzer = CallGraphAnalyzer()
        analyzer.build_from_ir(sample_ir_with_calls)

        output_path = temp_output_dir / "call_graph.json"
        analyzer.export_to_json(str(output_path))

        assert output_path.exists()

        # 验证 JSON 内容
        import json
        with open(output_path) as f:
            data = json.load(f)

        assert "analysis" in data
        assert "graph" in data
        assert data["analysis"]["total_functions"] == 4
