"""
核心数据模型 - Core Data Models

定义整个迁移系统共用的 Pydantic 数据模型，
确保各模块间数据传递的类型安全和一致性。

主要模型:
    - MigrationTask: 迁移任务配置
    - FileMapping: C 文件到 Java 文件的映射关系
    - TypeMapping: C 类型到 Java 类型的映射
    - MigrationReport: 迁移报告
    - IRFunction: IR 函数定义
    - IRStruct: IR 结构体定义
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


# =============================================================================
# 枚举类型
# =============================================================================

class MigrationStatus(str, Enum):
    """迁移任务状态"""
    PENDING = "pending"           # 待处理
    PARSING = "parsing"           # 解析中
    ANALYZING = "analyzing"       # 分析中
    TRANSLATING = "translating"   # 翻译中
    GENERATING = "generating"     # 生成中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class CallType(str, Enum):
    """函数调用类型"""
    DIRECT = "direct"             # 直接调用
    INDIRECT = "indirect"         # 间接调用 (函数指针)
    RECURSIVE = "recursive"       # 递归调用


class FileType(str, Enum):
    """文件类型"""
    C_SOURCE = "c_source"         # C 源文件
    C_HEADER = "c_header"         # C 头文件
    JAVA_SOURCE = "java_source"   # Java 源文件
    JAVA_CONFIG = "java_config"   # Java 配置文件


# =============================================================================
# IR 数据模型
# =============================================================================

class IRParameter(BaseModel):
    """IR 函数参数"""
    name: str
    type: str
    is_pointer: bool = False
    is_array: bool = False
    array_size: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "buffer",
                "type": "char",
                "is_pointer": True,
                "is_array": False
            }
        }


class IRCall(BaseModel):
    """IR 函数调用"""
    name: str
    line: int
    type: CallType = CallType.DIRECT
    is_external: bool = False  # 是否为外部函数 (如 printf)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "printf",
                "line": 10,
                "type": "direct",
                "is_external": True
            }
        }


class IRFunction(BaseModel):
    """
    IR 函数定义

    表示从 C 代码解析出的函数中间表示，
    包含函数签名、调用关系等完整信息。
    """
    name: str
    file_path: str
    line_number: int
    return_type: str
    parameters: List[IRParameter] = []
    calls: List[IRCall] = []
    local_variables: List[Dict[str, str]] = []
    body: Optional[str] = None  # 函数体原文
    is_static: bool = False
    is_inline: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "name": "add",
                "file_path": "math.c",
                "line_number": 5,
                "return_type": "int",
                "parameters": [
                    {"name": "a", "type": "int"},
                    {"name": "b", "type": "int"}
                ],
                "calls": [],
                "body": "return a + b;"
            }
        }


class IRField(BaseModel):
    """IR 结构体字段"""
    name: str
    type: str
    is_pointer: bool = False
    array_size: Optional[int] = None
    comment: Optional[str] = None


class IRStruct(BaseModel):
    """
    IR 结构体定义

    表示从 C 代码解析出的结构体中间表示。
    """
    name: str
    file_path: str
    line_number: int
    fields: List[IRField] = []
    typedef_alias: Optional[str] = None  # typedef 别名

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Order",
                "file_path": "order.h",
                "line_number": 10,
                "fields": [
                    {"name": "order_id", "type": "int"},
                    {"name": "price", "type": "double"}
                ],
                "typedef_alias": "Order"
            }
        }


class IREnumValue(BaseModel):
    """IR 枚举值"""
    name: str
    value: Optional[int] = None


class IREnum(BaseModel):
    """IR 枚举定义"""
    name: str
    file_path: str
    line_number: int
    values: List[IREnumValue] = []
    typedef_alias: Optional[str] = None


# =============================================================================
# 映射关系模型
# =============================================================================

class FileMapping(BaseModel):
    """
    C 文件到 Java 文件的映射

    记录源文件和目标文件的对应关系，
    用于增量迁移和结果追溯。
    """
    source_path: str              # C 源文件路径
    target_path: str              # Java 目标文件路径
    source_type: FileType = FileType.C_SOURCE
    target_type: FileType = FileType.JAVA_SOURCE
    status: MigrationStatus = MigrationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def mark_completed(self) -> None:
        """标记为已完成"""
        self.status = MigrationStatus.COMPLETED
        self.updated_at = datetime.now()

    def mark_failed(self) -> None:
        """标记为失败"""
        self.status = MigrationStatus.FAILED
        self.updated_at = datetime.now()


class TypeMapping(BaseModel):
    """
    C 类型到 Java 类型的映射

    定义 C 语言类型如何转换为 Java 类型，
    包括基本类型、指针、结构体等。
    """
    c_type: str                   # C 类型名
    java_type: str                # Java 类型名
    java_import: Optional[str] = None  # 需要的 import
    is_primitive: bool = True     # 是否为基本类型
    notes: Optional[str] = None   # 转换说明

    class Config:
        json_schema_extra = {
            "example": {
                "c_type": "int",
                "java_type": "int",
                "is_primitive": True
            }
        }


class FunctionMapping(BaseModel):
    """函数名映射关系"""
    c_name: str
    java_name: str
    mapping_type: str = "direct"  # direct, renamed, split, merged


class SymbolMapping(BaseModel):
    """符号映射 (函数、变量、类型)"""
    c_symbol: str
    java_symbol: str
    symbol_type: str  # function, variable, type, struct
    file_path: str


# =============================================================================
# 任务配置模型
# =============================================================================

class LLMConfig(BaseModel):
    """LLM 连接配置"""
    endpoint: str
    api_key: str
    model: str = "private-llm"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3

    class Config:
        json_schema_extra = {
            "example": {
                "endpoint": "http://localhost:8080/v1",
                "api_key": "your-api-key",
                "model": "private-llm-model"
            }
        }


class MigrationConfig(BaseModel):
    """
    迁移任务配置

    包含迁移过程的所有配置选项。
    """
    # 路径配置
    source_dir: str
    output_dir: str
    intermediate_dir: Optional[str] = None

    # LLM 配置
    llm: LLMConfig

    # 迁移策略
    skip_external_functions: bool = True    # 跳过外部函数
    generate_comments: bool = True          # 生成 JavaDoc 注释
    use_spring_boot: bool = True            # 使用 Spring Boot
    package_prefix: str = "com.migration"   # Java 包名前缀

    # 过滤配置
    include_patterns: List[str] = ["*.c", "*.h"]
    exclude_patterns: List[str] = ["*test*", "*mock*"]

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_dir": "data/input/c_source",
                "output_dir": "data/output/java_source",
                "llm": {
                    "endpoint": "http://localhost:8080/v1",
                    "api_key": "key",
                    "model": "private-llm"
                },
                "package_prefix": "com.securities"
            }
        }


# =============================================================================
# 报告模型
# =============================================================================

class AnalysisReport(BaseModel):
    """静态分析报告"""
    total_functions: int
    total_structs: int
    total_enums: int
    call_graph_nodes: int
    call_graph_edges: int
    recursive_functions: List[str]
    entry_points: List[str]
    external_dependencies: List[str]


class MigrationReport(BaseModel):
    """
    迁移完成报告

    记录迁移任务的执行结果和统计信息。
    """
    task_id: str
    config: MigrationConfig
    status: MigrationStatus
    start_time: datetime
    end_time: Optional[datetime] = None

    # 统计信息
    files_processed: int = 0
    functions_translated: int = 0
    structs_converted: int = 0
    errors: List[str] = []
    warnings: List[str] = []

    # 输出
    output_files: List[str] = []
    mapping_file: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """计算执行时长 (秒)"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def add_error(self, error: str) -> None:
        """添加错误信息"""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """添加警告信息"""
        self.warnings.append(warning)


# =============================================================================
# 导出所有公开模型
# =============================================================================

__all__ = [
    # 枚举
    "MigrationStatus",
    "CallType",
    "FileType",

    # IR 模型
    "IRParameter",
    "IRCall",
    "IRFunction",
    "IRField",
    "IRStruct",
    "IREnumValue",
    "IREnum",

    # 映射模型
    "FileMapping",
    "TypeMapping",
    "FunctionMapping",
    "SymbolMapping",

    # 配置模型
    "LLMConfig",
    "MigrationConfig",

    # 报告模型
    "AnalysisReport",
    "MigrationReport",
]
