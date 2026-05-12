"""
Java 代码写入器 - Java Code Writer

负责生成和写入 Java 源文件，包括：
    - Package 和 import 声明
    - 类/接口定义
    - 字段和方法
    - Spring 注解

使用示例:
    writer = JavaWriter(output_dir)
    writer.write_entity(entity_class)
"""

from .writer import JavaWriter

__all__ = ["JavaWriter"]
