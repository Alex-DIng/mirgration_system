"""
依赖分析模块 - Dependency Analysis

分析 C 源文件间的依赖关系，确定迁移批次和顺序。

主要功能:
    - 分析 #include 依赖
    - 分析全局变量依赖
    - 分析函数调用依赖
    - 生成迁移顺序建议

使用示例:
    analyzer = DependencyAnalyzer()
    order = analyzer.analyze(ir_functions, files)
"""

from .analyzer import DependencyAnalyzer, DependencyGraph

__all__ = ["DependencyAnalyzer", "DependencyGraph"]
