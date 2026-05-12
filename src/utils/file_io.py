"""
文件 I/O 工具 - File I/O Utilities
"""

import logging
from pathlib import Path
from typing import List, Optional, Iterator

logger = logging.getLogger(__name__)


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    读取文件内容

    Args:
        file_path: 文件路径
        encoding: 文件编码

    Returns:
        文件内容

    Raises:
        FileNotFoundError: 文件不存在
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r", encoding=encoding) as f:
        return f.read()


def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True
) -> None:
    """
    写入文件内容

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
        create_dirs: 是否自动创建父目录
    """
    path = Path(file_path)
    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding=encoding) as f:
        f.write(content)

    logger.debug(f"File written: {file_path}")


def find_files(
    directory: str,
    patterns: List[str],
    exclude_patterns: Optional[List[str]] = None
) -> Iterator[Path]:
    """
    查找匹配模式的文件

    Args:
        directory: 搜索目录
        patterns: 文件匹配模式列表 (如 ["*.c", "*.h"])
        exclude_patterns: 排除模式列表 (如 ["*test*", "*mock*"])

    Yields:
        匹配的文件路径
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    exclude = exclude_patterns or []

    for pattern in patterns:
        for file_path in dir_path.glob(pattern):
            # 检查是否需要排除
            should_exclude = any(
                file_path.match(excl) for excl in exclude
            )
            if not should_exclude:
                yield file_path


def get_file_size(file_path: str) -> int:
    """获取文件大小 (字节)"""
    return Path(file_path).stat().st_size


def get_file_line_count(file_path: str, encoding: str = "utf-8") -> int:
    """获取文件行数"""
    with open(file_path, "r", encoding=encoding) as f:
        return sum(1 for _ in f)


def backup_file(file_path: str, suffix: str = ".bak") -> str:
    """
    备份文件

    Args:
        file_path: 文件路径
        suffix: 备份文件后缀

    Returns:
        备份文件路径
    """
    path = Path(file_path)
    backup_path = path.with_suffix(path.suffix + suffix)
    path.rename(backup_path)
    return str(backup_path)
