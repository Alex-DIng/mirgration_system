"""
证券领域知识 - Securities Domain Knowledge

定义证券业务的核心概念和规则。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class OrderType:
    """订单类型"""
    name: str
    code: int
    description: str
    java_enum_name: str


@dataclass
class OrderStatus:
    """订单状态"""
    name: str
    code: int
    description: str
    java_enum_name: str


class SecuritiesKnowledge:
    """
    证券领域知识库

    提供证券业务相关的知识，用于指导代码翻译。
    """

    # 订单类型定义
    ORDER_TYPES = [
        OrderType(
            name="买入",
            code=1,
            description="买入证券订单",
            java_enum_name="BUY"
        ),
        OrderType(
            name="卖出",
            code=2,
            description="卖出证券订单",
            java_enum_name="SELL"
        ),
    ]

    # 订单状态定义
    ORDER_STATUSES = [
        OrderStatus(
            name="待报",
            code=0,
            description="订单已创建但尚未报送",
            java_enum_name="PENDING"
        ),
        OrderStatus(
            name="已报",
            code=1,
            description="订单已报送至交易所",
            java_enum_name="SUBMITTED"
        ),
        OrderStatus(
            name="成交",
            code=2,
            description="订单已全部或部分成交",
            java_enum_name="FILLED"
        ),
        OrderStatus(
            name="撤单",
            code=3,
            description="订单已被撤销",
            java_enum_name="CANCELLED"
        ),
        OrderStatus(
            name="废单",
            code=4,
            description="订单无效或被拒绝",
            java_enum_name="REJECTED"
        ),
    ]

    # C 类型到 Java 类型的映射
    TYPE_MAPPINGS = {
        "int": "Integer",
        "long": "Long",
        "float": "Float",
        "double": "Double",
        "char*": "String",
        "char[]": "String",
        "bool": "Boolean",
        "void*": "Object",
    }

    # 证券业务术语映射
    TERM_MAPPINGS = {
        "order": "订单",
        "stock": "证券/股票",
        "quantity": "数量",
        "price": "价格",
        "amount": "金额",
        "balance": "余额",
        "position": "持仓",
        "trade": "交易",
        "transaction": "成交",
        "cancel": "撤单",
        "submit": "申报",
        "match": "撮合",
        "market": "市场/行情",
        "quote": "行情",
        "bid": "买盘",
        "ask": "卖盘",
    }

    @classmethod
    def get_order_type_by_code(cls, code: int) -> Optional[OrderType]:
        """根据代码获取订单类型"""
        for ot in cls.ORDER_TYPES:
            if ot.code == code:
                return ot
        return None

    @classmethod
    def get_order_status_by_code(cls, code: int) -> Optional[OrderStatus]:
        """根据代码获取订单状态"""
        for os in cls.ORDER_STATUSES:
            if os.code == code:
                return os
        return None

    @classmethod
    def get_java_type(cls, c_type: str) -> str:
        """获取 C 类型对应的 Java 类型"""
        # 处理指针
        base_type = c_type.replace("*", "").replace("const", "").strip()
        return cls.TYPE_MAPPINGS.get(base_type, "Object")

    @classmethod
    def get_domain_context(cls) -> str:
        """
        获取领域知识上下文

        用于注入到 LLM 提示词中，提供业务背景。
        """
        return """
证券领域知识:

订单类型:
- BUY (1): 买入订单
- SELL (2): 卖出订单

订单状态:
- PENDING (0): 待报
- SUBMITTED (1): 已报
- FILLED (2): 成交
- CANCELLED (3): 撤单
- REJECTED (4): 废单

类型映射:
- int -> Integer
- long -> Long
- double -> Double
- char* -> String
- void* -> Object

业务规则:
1. 订单必须经过风控检查才能提交
2. 买入订单需要检查资金充足
3. 卖出订单需要检查持仓充足
4. 撤单只能对已报未成交的订单进行
""".strip()

    @classmethod
    def validate_business_logic(cls, java_code: str) -> List[str]:
        """
        验证 Java 代码是否符合业务规则

        Args:
            java_code: Java 代码

        Returns:
            违规列表
        """
        warnings = []

        # 检查订单状态变更是否合理
        if "setOrderStatus" in java_code:
            if "FILLED" not in java_code and "SUBMITTED" not in java_code:
                warnings.append("订单状态变更应包含 FILLED 或 SUBMITTED")

        return warnings
