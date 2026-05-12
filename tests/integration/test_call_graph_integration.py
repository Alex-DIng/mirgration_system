"""
调用图集成测试 - Call Graph Integration Tests

测试调用图模块与实际 C 源文件的集成。
"""

import pytest
from pathlib import Path

from src.analyzer.call_graph import CallGraph, CallGraphAnalyzer


@pytest.fixture
def call_graph_analyzer() -> CallGraphAnalyzer:
    """创建调用图分析器实例"""
    return CallGraphAnalyzer()


class TestCallGraphWithFixtures:
    """使用夹具文件的调用图测试"""

    def test_simple_function_graph(self, call_graph_analyzer):
        """测试简单函数的调用图"""
        ir_functions = [
            {
                "name": "main",
                "file_path": "simple.c",
                "line_number": 20,
                "calls": [
                    {"name": "add", "line": 25, "type": "direct"},
                    {"name": "subtract", "line": 26, "type": "direct"},
                ]
            },
            {
                "name": "add",
                "file_path": "simple.c",
                "line_number": 5,
                "calls": []
            },
            {
                "name": "subtract",
                "file_path": "simple.c",
                "line_number": 12,
                "calls": []
            }
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)
        report = call_graph_analyzer.analyze()

        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert report["total_functions"] == 3
        assert report["total_calls"] == 2

    def test_recursive_function_detection(self, call_graph_analyzer):
        """测试递归函数检测"""
        ir_functions = [
            {
                "name": "factorial",
                "file_path": "recursive.c",
                "line_number": 1,
                "calls": [
                    {"name": "factorial", "line": 6, "type": "recursive"}
                ]
            }
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)
        recursive_funcs = graph.find_recursive_functions()

        assert "factorial" in recursive_funcs
        assert graph.nodes["factorial"].is_recursive is True

    def test_indirect_recursion_detection(self, call_graph_analyzer):
        """测试间接递归检测（A -> B -> A）"""
        ir_functions = [
            {
                "name": "func_a",
                "file_path": "mutual.c",
                "line_number": 1,
                "calls": [{"name": "func_b", "line": 5, "type": "direct"}]
            },
            {
                "name": "func_b",
                "file_path": "mutual.c",
                "line_number": 10,
                "calls": [{"name": "func_a", "line": 14, "type": "direct"}]
            }
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)
        recursive_funcs = graph.find_recursive_functions()

        assert "func_a" in recursive_funcs
        assert "func_b" in recursive_funcs

    def test_call_chain_detection(self, call_graph_analyzer):
        """测试调用链检测"""
        ir_functions = [
            {"name": "main", "file_path": "chain.c", "line_number": 1,
             "calls": [{"name": "level1", "line": 5, "type": "direct"}]},
            {"name": "level1", "file_path": "chain.c", "line_number": 10,
             "calls": [{"name": "level2", "line": 14, "type": "direct"}]},
            {"name": "level2", "file_path": "chain.c", "line_number": 20,
             "calls": [{"name": "level3", "line": 24, "type": "direct"}]},
            {"name": "level3", "file_path": "chain.c", "line_number": 30, "calls": []}
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        chains = graph.get_call_chain("main", "level3")

        assert len(chains) > 0
        assert ["main", "level1", "level2", "level3"] in chains

    def test_entry_point_detection(self, call_graph_analyzer):
        """测试入口函数检测"""
        ir_functions = [
            {"name": "main", "file_path": "main.c", "line_number": 1,
             "calls": [{"name": "helper", "line": 5, "type": "direct"}]},
            {"name": "helper", "file_path": "helper.c", "line_number": 10, "calls": []}
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        entry_points = graph.get_entry_points()

        assert len(entry_points) == 1
        assert entry_points[0].name == "main"
        assert graph.nodes["main"].is_entry_point is True

    def test_leaf_function_detection(self, call_graph_analyzer):
        """测试叶子函数检测"""
        ir_functions = [
            {"name": "main", "file_path": "main.c", "line_number": 1,
             "calls": [{"name": "pure_func", "line": 5, "type": "direct"}]},
            {"name": "pure_func", "file_path": "utils.c", "line_number": 10, "calls": []}
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        leaf_funcs = graph.get_leaf_functions()

        assert len(leaf_funcs) == 1
        assert leaf_funcs[0].name == "pure_func"

    def test_call_depth_calculation(self, call_graph_analyzer):
        """测试调用深度计算"""
        ir_functions = [
            {"name": "main", "file_path": "depth.c", "line_number": 1,
             "calls": [{"name": "func_a", "line": 5, "type": "direct"}]},
            {"name": "func_a", "file_path": "depth.c", "line_number": 10,
             "calls": [{"name": "func_b", "line": 14, "type": "direct"}]},
            {"name": "func_b", "file_path": "depth.c", "line_number": 20,
             "calls": [{"name": "func_c", "line": 24, "type": "direct"}]},
            {"name": "func_c", "file_path": "depth.c", "line_number": 30, "calls": []}
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        depth = graph.compute_call_depth("main")

        assert depth == 4  # main -> func_a -> func_b -> func_c

    def test_json_export(self, call_graph_analyzer, temp_output_dir):
        """测试 JSON 导出"""
        ir_functions = [
            {"name": "test_func", "file_path": "test.c", "line_number": 1, "calls": []}
        ]

        call_graph_analyzer.build_from_ir(ir_functions)

        output_path = temp_output_dir / "call_graph.json"
        call_graph_analyzer.export_to_json(str(output_path))

        assert output_path.exists()

        import json
        with open(output_path) as f:
            data = json.load(f)

        assert "analysis" in data
        assert "graph" in data
        assert data["analysis"]["total_functions"] == 1


class TestCallGraphEdgeCases:
    """调用图边界情况测试"""

    def test_empty_ir(self, call_graph_analyzer):
        """测试空 IR 输入"""
        graph = call_graph_analyzer.build_from_ir([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_single_function_no_calls(self, call_graph_analyzer):
        """测试单个函数无调用"""
        ir_functions = [
            {"name": "standalone", "file_path": "single.c", "line_number": 1, "calls": []}
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)
        report = call_graph_analyzer.analyze()

        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0
        assert report["total_functions"] == 1
        assert report["total_calls"] == 0

    def test_external_function_calls(self, call_graph_analyzer):
        """测试外部函数调用（如 printf）"""
        ir_functions = [
            {
                "name": "main",
                "file_path": "main.c",
                "line_number": 1,
                "calls": [
                    {"name": "printf", "line": 5, "type": "direct"},
                    {"name": "malloc", "line": 6, "type": "direct"},
                ]
            }
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        # 外部関数はノードとして追加されないが、エッジとして記録される
        # main 関数の callees に外部関数名が含まれる
        assert "main" in graph.nodes
        main_node = graph.nodes["main"]
        assert "printf" in main_node.callees
        assert "malloc" in main_node.callees

    def test_function_pointer_call(self, call_graph_analyzer):
        """测试函数指针调用"""
        ir_functions = [
            {
                "name": "sort_array",
                "file_path": "sort.c",
                "line_number": 1,
                "calls": [
                    {"name": "compare_func", "line": 10, "type": "indirect"}
                ]
            }
        ]

        graph = call_graph_analyzer.build_from_ir(ir_functions)

        # 查找间接调用
        report = call_graph_analyzer.analyze()
        assert len(report["indirect_calls"]) > 0
