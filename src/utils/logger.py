"""
日志工具 - Logger Utilities
"""

import logging
import sys
from typing import Optional
from pathlib import Path


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 记录器名称
        level: 日志级别
        log_file: 日志文件路径 (可选)
        format_string: 日志格式 (可选)

    Returns:
        配置好的 Logger 实例
    """
    if format_string is None:
        format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除已有 handler
    logger.handlers.clear()

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(console_handler)

    # 文件 handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    return logger
