"""
迁移流水线模块 - Migration Pipeline

编排整个 C 到 Java 的迁移流程：
    解析 → 分析 → 翻译 → 生成

核心类:
    MigrationPipeline: 主流水线编排器
"""

from .pipeline import MigrationPipeline

__all__ = ["MigrationPipeline"]
