"""
CLI Module

Command-line interface for the migration system with subcommands:
    - migrate: Execute full migration
    - parse: Parse C source files only
    - analyze: Analyze call graph only
    - generate: Generate Java code only
    - config: Manage configuration files

Usage:
    python -m src.cli migrate --source ./c_source --output ./java_output
"""

from .main import cli

__all__ = ["cli"]
