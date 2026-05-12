"""
代码生成模块 - Code Generator

将 LLM 翻译结果转换为符合 Spring 框架规范的 Java 代码：
    - java_writer: Java 代码写入器
    - templates: Jinja2 代码模板

使用示例:
    from src.generator.java_writer import JavaWriter

    writer = JavaWriter(output_dir="data/output")
    writer.generate_entity(entity_data)
"""

from . import java_writer
from . import templates

__all__ = ["java_writer", "templates"]
