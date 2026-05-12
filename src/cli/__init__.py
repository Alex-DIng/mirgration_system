"""
命令行接口模块 - CLI Module

提供迁移系统的命令行入口，支持以下子命令：
    - migrate: 执行完整迁移流程
    - parse: 仅解析 C 源码
    - analyze: 仅执行分析
    - generate: 仅生成 Java 代码
    - config: 管理配置文件

使用示例:
    python -m src.cli migrate --source ./c_source --output ./java_output
"""

from .main import cli

__all__ = ["cli"]
