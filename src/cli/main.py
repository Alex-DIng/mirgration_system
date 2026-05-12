"""
命令行主程序 - CLI Main Program

实现迁移系统的命令行接口。
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from src.core.models import MigrationConfig, LLMConfig
from src.core.pipeline import MigrationPipeline


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """设置日志"""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def cmd_migrate(args: argparse.Namespace) -> int:
    """执行迁移命令"""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting migration from {args.source} to {args.output}")

    # 构建配置
    llm_config = LLMConfig(
        endpoint=args.llm_endpoint or "http://localhost:8080/v1",
        api_key=args.llm_key or "default-key",
        model=args.llm_model or "private-llm",
    )

    config = MigrationConfig(
        source_dir=args.source,
        output_dir=args.output,
        llm=llm_config,
        package_prefix=args.package_prefix or "com.migration",
    )

    try:
        # 执行迁移
        pipeline = MigrationPipeline(config)
        report = pipeline.run()

        logger.info(f"Migration completed: {report.files_processed} files processed")
        return 0

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        return 1


def cmd_parse(args: argparse.Namespace) -> int:
    """执行解析命令"""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    from src.parser.c_parser import CParser

    parser = CParser()

    source_path = Path(args.source)
    if source_path.is_file():
        result = parser.parse_file(str(source_path))
        logger.info(f"Parsed file: {source_path}")
    elif source_path.is_dir():
        result = parser.parse_directory(str(source_path))
        logger.info(f"Parsed directory: {source_path}")
    else:
        logger.error(f"Source not found: {source_path}")
        return 1

    logger.info(f"Found {len(result.get('functions', []))} functions")
    logger.info(f"Found {len(result.get('structs', []))} structs")
    logger.info(f"Found {len(result.get('enums', []))} enums")

    # 导出 IR
    if args.output:
        import json
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"IR exported to: {output_path}")

    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """执行分析命令"""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # 先解析
    from src.parser.c_parser import CParser
    from src.analyzer.call_graph import CallGraphAnalyzer

    parser = CParser()
    result = parser.parse_directory(args.source)

    # 构建调用图
    analyzer = CallGraphAnalyzer()
    graph = analyzer.build_from_ir(result.get("functions", []))
    report = analyzer.analyze()

    logger.info(f"Total functions: {report['total_functions']}")
    logger.info(f"Total calls: {report['total_calls']}")
    logger.info(f"Entry points: {report['entry_points']}")
    logger.info(f"Recursive functions: {report['recursive_functions']}")

    if args.output:
        analyzer.export_to_json(args.output)
        logger.info(f"Analysis exported to: {args.output}")

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """配置管理命令"""
    config_dir = Path.home() / ".migration_system"
    config_dir.mkdir(parents=True, exist_ok=True)

    if args.action == "init":
        # 创建示例配置
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            print(f"Config already exists: {config_file}")
        else:
            config_content = """# Migration System Configuration

llm:
  endpoint: http://localhost:8080/v1
  api_key: your-api-key-here
  model: private-llm-model
  max_tokens: 4096
  temperature: 0.7

migration:
  package_prefix: com.migration
  generate_comments: true
  use_spring_boot: true

logging:
  level: INFO
  file: migration.log
"""
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)
            print(f"Config created: {config_file}")

    elif args.action == "show":
        config_file = config_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("No config file found. Run 'config init' first.")

    return 0


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="migration-system",
        description="C 到 Java 证券交易系统迁移工具",
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # migrate 命令
    migrate_parser = subparsers.add_parser("migrate", help="执行完整迁移")
    migrate_parser.add_argument("--source", "-s", required=True, help="C 源码目录")
    migrate_parser.add_argument("--output", "-o", required=True, help="Java 输出目录")
    migrate_parser.add_argument("--llm-endpoint", help="LLM API 端点")
    migrate_parser.add_argument("--llm-key", help="LLM API 密钥")
    migrate_parser.add_argument("--llm-model", help="LLM 模型名称")
    migrate_parser.add_argument("--package-prefix", default="com.migration", help="Java 包名前缀")
    migrate_parser.add_argument("--log-level", default="INFO", help="日志级别")
    migrate_parser.set_defaults(func=cmd_migrate)

    # parse 命令
    parse_parser = subparsers.add_parser("parse", help="解析 C 源码")
    parse_parser.add_argument("--source", "-s", required=True, help="C 源码文件/目录")
    parse_parser.add_argument("--output", "-o", help="IR 输出文件")
    parse_parser.add_argument("--log-level", default="INFO", help="日志级别")
    parse_parser.set_defaults(func=cmd_parse)

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析调用图")
    analyze_parser.add_argument("--source", "-s", required=True, help="C 源码目录")
    analyze_parser.add_argument("--output", "-o", help="分析报告输出")
    analyze_parser.add_argument("--log-level", default="INFO", help="日志级别")
    analyze_parser.set_defaults(func=cmd_analyze)

    # config 命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_parser.add_argument(
        "action",
        choices=["init", "show"],
        help="配置操作",
    )
    config_parser.set_defaults(func=cmd_config)

    return parser


def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


# 命令行入口
cli = main

if __name__ == "__main__":
    sys.exit(main())
