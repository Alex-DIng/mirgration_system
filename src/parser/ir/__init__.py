"""
中间表示模块 - Intermediate Representation (IR)

定义与语言无关的中间表示结构，
用于在解析、分析、翻译和生成阶段之间传递数据。

主要类:
    IRFunction: 函数 IR
    IRStruct: 结构体 IR
    IREnum: 枚举 IR
    IRType: 类型 IR
"""

from src.core.models import (
    IRFunction,
    IRStruct,
    IREnum,
    IRParameter,
    IRField,
    IRCall,
    IREnumValue,
)

__all__ = [
    "IRFunction",
    "IRStruct",
    "IREnum",
    "IRParameter",
    "IRField",
    "IRCall",
    "IREnumValue",
]
