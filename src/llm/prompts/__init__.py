"""
提示词模板模块 - Prompt Templates

管理 C 到 Java 翻译的提示词模板：
    - 函数翻译模板
    - 结构体转换模板
    - 带上下文分析的翻译模板

使用示例:
    from src.llm.prompts import PromptTemplate

    template = PromptTemplate.load("c_to_java/function")
    prompt = template.render(c_code="int add(...) {...}")
"""

from .templates import PromptTemplate, PromptTemplateManager

__all__ = ["PromptTemplate", "PromptTemplateManager"]
