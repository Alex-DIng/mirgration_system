"""
Migration System - C 到 Java 证券交易系统迁移工具

利用私有大语言模型 (Private LLM) 将大型 C 语言证券交易系统
自动化迁移为 Spring 框架 Java 项目。

工作流程:
    C 源码 → 解析 (AST/IR) → 静态分析 → LLM 翻译 → Java 代码生成 → Spring 项目

主要模块:
    - parser: C 语言解析器，生成中间表示 (IR)
    - analyzer: 静态分析器 (调用图、数据流、依赖分析)
    - llm: 私有大模型集成，负责语义理解和代码翻译
    - generator: Java 代码生成器，输出 Spring 规范代码
    - knowledge: 领域知识库 (证券业务 + Spring 框架)
    - cli: 命令行入口

示例用法:
    from src.core.pipeline import MigrationPipeline

    pipeline = MigrationPipeline(config)
    result = pipeline.run(
        source_dir="data/input/c_source",
        output_dir="data/output/java_source"
    )
"""

__version__ = "0.1.0"
__author__ = "Migration System Team"
