"""
知识库模块 - Knowledge Base

提供领域知识，减少 LLM 幻觉，确保翻译正确性：
    - securities: 证券领域知识 (交易规则、订单类型、风控逻辑)
    - spring: Spring 框架知识 (Bean 生命周期、事务管理、JPA 映射)

知识库在翻译过程中被引用，确保生成的 Java 代码符合领域规范。
"""

from . import securities
from . import spring

__all__ = ["securities", "spring"]
