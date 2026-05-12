"""
命令行入口 - CLI Entry Point

支持通过 python -m src.cli 运行
"""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
