"""
CLI Main Program

Implements the command-line interface for the migration system.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from src.core.models import MigrationConfig, LLMConfig
from src.core.pipeline import MigrationPipeline


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging"""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def cmd_migrate(args: argparse.Namespace) -> int:
    """Execute migration command"""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    logger.info(f"Starting migration from {args.source} to {args.output}")

    # Build config
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
        # Execute migration
        pipeline = MigrationPipeline(config)
        report = pipeline.run()

        logger.info(f"Migration completed: {report.files_processed} files processed")
        return 0

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        return 1


def cmd_parse(args: argparse.Namespace) -> int:
    """Execute parse command"""
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

    # Export IR
    if args.output:
        import json
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"IR exported to: {output_path}")

    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute analyze command"""
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Parse first
    from src.parser.c_parser import CParser
    from src.analyzer.call_graph import CallGraphAnalyzer

    parser = CParser()
    result = parser.parse_directory(args.source)

    # Build call graph
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
    """Config management command"""
    config_dir = Path.home() / ".migration_system"
    config_dir.mkdir(parents=True, exist_ok=True)

    if args.action == "init":
        # Create sample config
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
    """Create CLI parser"""
    parser = argparse.ArgumentParser(
        prog="migration-system",
        description="C to Java Trading System Migration Tool",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Execute full migration")
    migrate_parser.add_argument("--source", "-s", required=True, help="C source directory")
    migrate_parser.add_argument("--output", "-o", required=True, help="Java output directory")
    migrate_parser.add_argument("--llm-endpoint", help="LLM API endpoint")
    migrate_parser.add_argument("--llm-key", help="LLM API key")
    migrate_parser.add_argument("--llm-model", help="LLM model name")
    migrate_parser.add_argument("--package-prefix", default="com.migration", help="Java package prefix")
    migrate_parser.add_argument("--log-level", default="INFO", help="Log level")
    migrate_parser.set_defaults(func=cmd_migrate)

    # parse command
    parse_parser = subparsers.add_parser("parse", help="Parse C source files")
    parse_parser.add_argument("--source", "-s", required=True, help="C source file/directory")
    parse_parser.add_argument("--output", "-o", help="IR output file")
    parse_parser.add_argument("--log-level", default="INFO", help="Log level")
    parse_parser.set_defaults(func=cmd_parse)

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze call graph")
    analyze_parser.add_argument("--source", "-s", required=True, help="C source directory")
    analyze_parser.add_argument("--output", "-o", help="Analysis report output")
    analyze_parser.add_argument("--log-level", default="INFO", help="Log level")
    analyze_parser.set_defaults(func=cmd_analyze)

    # config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "action",
        choices=["init", "show"],
        help="Config action",
    )
    config_parser.set_defaults(func=cmd_config)

    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


# CLI entry point
cli = main

if __name__ == "__main__":
    sys.exit(main())
