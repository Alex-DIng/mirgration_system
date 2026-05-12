"""
证券领域知识模块 - Securities Domain Knowledge

包含证券业务规则、交易规则、订单类型、风控逻辑等知识。
这些知识用于指导 LLM 正确理解 C 代码中的业务语义。

主要知识:
    - 订单类型 (买入、卖出、市价单、限价单)
    - 订单状态 (待报、已报、成交、撤单、废单)
    - 交易规则 (集合竞价、连续竞价)
    - 风控规则 (持仓限制、资金检查)
"""

from .domain import SecuritiesKnowledge

__all__ = ["SecuritiesKnowledge"]
