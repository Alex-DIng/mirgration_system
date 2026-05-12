"""
C 语言解析器实现 - C Parser Implementation
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.models import IRFunction, IRStruct, IREnum

logger = logging.getLogger(__name__)


class CParser:
    """
    C 语言解析器

    使用 tree-sitter 解析 C 源码，生成 IR 表示。

    功能:
        - 解析单个文件或目录
        - 提取函数、结构体、枚举定义
        - 识别函数调用关系
        - 处理头文件包含

    示例:
        parser = CParser()
        result = parser.parse_file("example.c")
        print(f"Found {len(result.functions)} functions")
    """

    def __init__(self):
        """初始化解析器"""
        self._tree_sitter_initialized = False
        self._language = None
        self._parser = None

    def _ensure_tree_sitter(self) -> None:
        """确保 tree-sitter 已初始化"""
        if not self._tree_sitter_initialized:
            try:
                from tree_sitter import Language, Parser

                # 加载 C 语言语法
                # 需要先运行：git clone https://github.com/tree-sitter/tree-sitter-c
                self._language = Language("tree-sitter-c.so", "c")
                self._parser = Parser()
                self._parser.set_language(self._language)
                self._tree_sitter_initialized = True
            except ImportError:
                logger.warning("tree-sitter not available, using fallback parser")

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析单个 C 文件

        Args:
            file_path: C 文件路径

        Returns:
            包含 functions, structs, enums 的字典
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Parsing file: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            source_code = f.read()

        return self.parse(source_code, str(path))

    def parse_directory(
        self,
        dir_path: str,
        patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        解析目录下的所有 C 文件

        Args:
            dir_path: 目录路径
            patterns: 文件匹配模式，默认 ["*.c", "*.h"]

        Returns:
            累积的解析结果
        """
        patterns = patterns or ["*.c", "*.h"]
        dir_path = Path(dir_path)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        all_functions = []
        all_structs = []
        all_enums = []
        files_processed = 0

        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                try:
                    result = self.parse_file(str(file_path))
                    all_functions.extend(result.get("functions", []))
                    all_structs.extend(result.get("structs", []))
                    all_enums.extend(result.get("enums", []))
                    files_processed += 1
                except Exception as e:
                    logger.error(f"Failed to parse {file_path}: {e}")

        return {
            "functions": all_functions,
            "structs": all_structs,
            "enums": all_enums,
            "files_processed": files_processed,
        }

    def parse(self, source_code: str, file_path: str = "<unknown>") -> Dict[str, Any]:
        """
        解析 C 源码字符串

        Args:
            source_code: C 源码
            file_path: 源文件路径 (用于错误报告)

        Returns:
            解析结果字典
        """
        self._ensure_tree_sitter()

        functions = self._parse_functions(source_code, file_path)
        structs = self._parse_structs(source_code, file_path)
        enums = self._parse_enums(source_code, file_path)

        return {
            "functions": functions,
            "structs": structs,
            "enums": enums,
            "file_path": file_path,
        }

    def _parse_functions(
        self,
        source_code: str,
        file_path: str
    ) -> List[IRFunction]:
        """
        解析函数定义

        Args:
            source_code: C 源码
            file_path: 文件路径

        Returns:
            IRFunction 列表
        """
        # TODO: 使用 tree-sitter 实现真正的解析
        # 这里提供基于正则的简化实现作为占位

        import re

        functions = []

        # 简化的函数匹配正则
        func_pattern = re.compile(
            r'^(\w+(?:\s*\*)?)\s+(\w+)\s*\(([^)]*)\)\s*\{',
            re.MULTILINE
        )

        for match in func_pattern.finditer(source_code):
            return_type = match.group(1).strip()
            func_name = match.group(2).strip()
            params_str = match.group(3).strip()

            # 跳过预处理指令
            if func_name in ("if", "while", "for", "switch"):
                continue

            # 解析参数
            parameters = self._parse_parameters(params_str)

            # 计算行号
            line_number = source_code[:match.start()].count("\n") + 1

            func = IRFunction(
                name=func_name,
                file_path=file_path,
                line_number=line_number,
                return_type=return_type,
                parameters=parameters,
            )

            functions.append(func)

        logger.debug(f"Found {len(functions)} functions in {file_path}")
        return functions

    def _parse_parameters(self, params_str: str) -> List:
        """
        解析函参数字符串

        Args:
            params_str: 参数字符串，如 "int a, char* b"

        Returns:
            IRParameter 列表
        """
        from src.core.models import IRParameter

        parameters = []

        if not params_str or params_str == "void":
            return parameters

        # 按逗号分割参数
        for param in params_str.split(","):
            param = param.strip()
            if not param:
                continue

            parts = param.split()
            if len(parts) >= 2:
                # 处理指针
                param_type = parts[0].strip()
                param_name = parts[-1].strip()
                is_pointer = "*" in param

                parameters.append(IRParameter(
                    name=param_name,
                    type=param_type,
                    is_pointer=is_pointer,
                ))

        return parameters

    def _parse_structs(
        self,
        source_code: str,
        file_path: str
    ) -> List[IRStruct]:
        """
        解析结构体定义

        Args:
            source_code: C 源码
            file_path: 文件路径

        Returns:
            IRStruct 列表
        """
        import re

        structs = []

        # 匹配 struct 定义
        struct_pattern = re.compile(
            r'typedef\s+struct\s*\{([^}]+)\}\s*(\w+);',
            re.MULTILINE | re.DOTALL
        )

        for match in struct_pattern.finditer(source_code):
            body = match.group(1)
            typedef_name = match.group(2)

            line_number = source_code[:match.start()].count("\n") + 1
            fields = self._parse_struct_fields(body)

            struct = IRStruct(
                name=typedef_name,
                file_path=file_path,
                line_number=line_number,
                fields=fields,
                typedef_alias=typedef_name,
            )

            structs.append(struct)

        logger.debug(f"Found {len(structs)} structs in {file_path}")
        return structs

    def _parse_struct_fields(self, body: str) -> List:
        """
        解析结构体字段

        Args:
            body: 结构体内容

        Returns:
            IRField 列表
        """
        from src.core.models import IRField
        import re

        fields = []

        for line in body.strip().split("\n"):
            line = line.strip().rstrip(";")
            if not line or line.startswith("//"):
                continue

            parts = line.split()
            if len(parts) >= 2:
                field_type = parts[0].strip()
                field_name_raw = parts[-1].strip()

                # 配列名の解析（例：name[64] -> name, array_size=64）
                array_match = re.match(r'(\w+)\[(\d+)\]', field_name_raw)
                if array_match:
                    field_name = array_match.group(1)
                    array_size = int(array_match.group(2))
                else:
                    field_name = field_name_raw
                    array_size = None

                fields.append(IRField(
                    name=field_name,
                    type=field_type,
                    array_size=array_size,
                ))

        return fields

    def _parse_enums(
        self,
        source_code: str,
        file_path: str
    ) -> List[IREnum]:
        """
        解析枚举定义

        Args:
            source_code: C 源码
            file_path: 文件路径

        Returns:
            IREnum 列表
        """
        import re

        enums = []

        # 匹配 enum 定义
        enum_pattern = re.compile(
            r'typedef\s+enum\s*\{([^}]+)\}\s*(\w+);',
            re.MULTILINE | re.DOTALL
        )

        for match in enum_pattern.finditer(source_code):
            body = match.group(1)
            typedef_name = match.group(2)

            line_number = source_code[:match.start()].count("\n") + 1
            values = self._parse_enum_values(body)

            from src.core.models import IREnum, IREnumValue
            enum = IREnum(
                name=typedef_name,
                file_path=file_path,
                line_number=line_number,
                values=values,
                typedef_alias=typedef_name,
            )

            enums.append(enum)

        logger.debug(f"Found {len(enums)} enums in {file_path}")
        return enums

    def _parse_enum_values(self, body: str) -> List:
        """
        解析枚举值

        Args:
            body: 枚举体内容

        Returns:
            IREnumValue 列表
        """
        from src.core.models import IREnumValue

        values = []
        current_value = 0

        for line in body.strip().split("\n"):
            line = line.strip().rstrip(",")
            if not line or line.startswith("//"):
                continue

            parts = line.split("=")
            name = parts[0].strip()

            if len(parts) > 1:
                try:
                    current_value = int(parts[1].strip())
                except ValueError:
                    pass

            values.append(IREnumValue(name=name, value=current_value))
            current_value += 1

        return values
