"""
C 语言解析器单元测试 - C Parser Unit Tests

测试覆盖：
- 函数定义解析 (基于正则的 fallback 实现)
- 结构体解析
- 枚举解析
- 参数解析 (包括指针类型)
- 文件解析和目录解析

注意：当前实现使用基于正则的 fallback 解析器，
tree-sitter 集成后可获得更精确的 AST 解析。
"""

import pytest
from pathlib import Path

from src.parser.c_parser import CParser
from src.core.models import IRFunction, IRStruct, IREnum, IRParameter, IRField, IREnumValue


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def parser() -> CParser:
    """创建 CParser 实例"""
    return CParser()


@pytest.fixture
def simple_c_code() -> str:
    """简单 C 代码样例"""
    return """
int add(int a, int b) {
    return a + b;
}

void greet(const char* name) {
    printf("Hello, %s!\\n", name);
}
"""


@pytest.fixture
def struct_c_code() -> str:
    """包含结构体的 C 代码"""
    return """
typedef struct {
    int id;
    char name[64];
    double balance;
} Account;

typedef struct {
    Account* accounts;
    int count;
} AccountList;
"""


@pytest.fixture
def enum_c_code() -> str:
    """包含枚举的 C 代码"""
    return """
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR = 1,
    STATUS_PENDING = 2
} Status;

typedef enum {
    TYPE_BUY,
    TYPE_SELL
} OrderType;
"""


@pytest.fixture
def sample_c_file(tmp_path: Path) -> Path:
    """创建临时 C 文件"""
    content = """
int multiply(int a, int b) {
    return a * b;
}

typedef struct {
    int x;
    int y;
} Point;
"""
    file_path = tmp_path / "sample.c"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def sample_c_dir(tmp_path: Path) -> Path:
    """创建临时 C 文件目录"""
    dir_path = tmp_path / "c_source"
    dir_path.mkdir()

    (dir_path / "file1.c").write_text("""
int func1() { return 1; }
""", encoding="utf-8")

    (dir_path / "file2.c").write_text("""
int func2() { return 2; }
""", encoding="utf-8")

    return dir_path


# =============================================================================
# CParser 初始化测试
# =============================================================================

class TestCParserInit:
    """CParser 初始化测试"""

    def test_create_parser(self, parser):
        """测试创建解析器实例"""
        assert parser is not None
        assert parser._tree_sitter_initialized is False

    def test_parser_lazy_initialization(self, parser):
        """测试 tree-sitter 延迟初始化"""
        # 创建时不应初始化
        assert parser._language is None
        assert parser._parser is None


# =============================================================================
# 函数解析测试
# =============================================================================

class TestParseFunctions:
    """函数解析测试"""

    def test_parse_simple_function(self, parser, simple_c_code):
        """测试解析简单函数"""
        result = parser.parse(simple_c_code, "test.c")

        functions = result.get("functions", [])
        assert len(functions) == 2

        # 检查第一个函数
        func = functions[0]
        assert isinstance(func, IRFunction)
        assert func.name == "add"
        assert func.return_type == "int"
        assert func.file_path == "test.c"

    def test_parse_function_with_pointer_param(self, parser):
        """测试解析带指针参数的函数"""
        code = """
void process(char* buffer, int* size) {
    // ...
}
"""
        result = parser.parse(code, "test.c")
        functions = result.get("functions", [])

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "process"

        # 检查指针参数
        params = func.parameters
        assert len(params) == 2
        assert params[0].name == "buffer"
        assert params[0].is_pointer is True
        assert params[1].name == "size"
        assert params[1].is_pointer is True

    def test_parse_function_void_params(self, parser):
        """测试解析 void 参数函数"""
        code = """
void init(void) {
    // ...
}
"""
        result = parser.parse(code, "test.c")
        functions = result.get("functions", [])

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "init"
        assert len(func.parameters) == 0

    def test_parse_function_line_number(self, parser):
        """测试函数行号计算"""
        code = """
// 注释行
// 注释行

int target_func(int x) {
    return x;
}
"""
        result = parser.parse(code, "test.c")
        functions = result.get("functions", [])

        assert len(functions) == 1
        func = functions[0]
        assert func.line_number == 5  # 第 5 行

    def test_parse_skip_control_flow(self, parser):
        """测试跳过控制流关键字"""
        code = """
int real_func() {
    if (x > 0) {
        while (x > 0) {
            for (int i = 0; i < x; i++) {
                switch (x) {
                }
            }
        }
    }
    return 0;
}
"""
        result = parser.parse(code, "test.c")
        functions = result.get("functions", [])

        # 只应识别 real_func，不应识别 if/while/for/switch
        assert len(functions) == 1
        assert functions[0].name == "real_func"


# =============================================================================
# 参数解析测试
# =============================================================================

class TestParseParameters:
    """参数解析测试"""

    def test_parse_single_parameter(self, parser):
        """测试解析单个参数"""
        code = "int func(int a) { return a; }"
        result = parser.parse(code, "test.c")
        func = result["functions"][0]

        assert len(func.parameters) == 1
        param = func.parameters[0]
        assert param.name == "a"
        assert param.type == "int"
        assert param.is_pointer is False

    def test_parse_multiple_parameters(self, parser):
        """测试解析多个参数"""
        code = "int func(int a, int b, int c) { return a + b + c; }"
        result = parser.parse(code, "test.c")
        func = result["functions"][0]

        assert len(func.parameters) == 3
        assert func.parameters[0].name == "a"
        assert func.parameters[1].name == "b"
        assert func.parameters[2].name == "c"

    def test_parse_pointer_parameter_detection(self, parser):
        """测试指针参数检测"""
        code = "void func(char* str, const int* value) { }"
        result = parser.parse(code, "test.c")
        func = result["functions"][0]

        assert len(func.parameters) == 2
        assert func.parameters[0].is_pointer is True
        assert func.parameters[1].is_pointer is True

    def test_parse_parameter_type(self, parser):
        """测试参数类型解析"""
        params_str = "int a"
        params = parser._parse_parameters(params_str)

        assert len(params) == 1
        assert params[0].type == "int"
        assert params[0].name == "a"


# =============================================================================
# 结构体解析测试
# =============================================================================

class TestParseStructs:
    """结构体解析测试"""

    def test_parse_single_struct(self, parser, struct_c_code):
        """测试解析单个结构体"""
        result = parser.parse(struct_c_code, "test.c")

        structs = result.get("structs", [])
        assert len(structs) == 2

        # 检查第一个结构体
        struct = structs[0]
        assert isinstance(struct, IRStruct)
        assert struct.name == "Account"
        assert struct.typedef_alias == "Account"

    def test_parse_struct_fields(self, parser, struct_c_code):
        """测试解析结构体字段"""
        result = parser.parse(struct_c_code, "test.c")
        structs = result.get("structs", [])

        assert len(structs) > 0
        struct = structs[0]  # Account

        assert len(struct.fields) == 3
        assert struct.fields[0].name == "id"
        assert struct.fields[0].type == "int"
        assert struct.fields[1].name == "name"
        assert struct.fields[2].name == "balance"
        assert struct.fields[2].type == "double"

    def test_parse_struct_line_number(self, parser):
        """测试结构体行号计算"""
        code = """
// 注释

typedef struct {
    int x;
} MyStruct;
"""
        result = parser.parse(code, "test.c")
        structs = result.get("structs", [])

        assert len(structs) == 1
        assert structs[0].line_number == 4

    def test_parse_struct_field_parsing(self, parser):
        """测试字段解析辅助方法"""
        body = """
    int id;
    char name[64];
    double balance;
"""
        fields = parser._parse_struct_fields(body)

        assert len(fields) == 3
        assert fields[0].name == "id"
        assert fields[1].name == "name"
        assert fields[2].name == "balance"


# =============================================================================
# 枚举解析测试
# =============================================================================

class TestParseEnums:
    """枚举解析测试"""

    def test_parse_single_enum(self, parser, enum_c_code):
        """测试解析单个枚举"""
        result = parser.parse(enum_c_code, "test.c")

        enums = result.get("enums", [])
        assert len(enums) == 2

        # 检查第一个枚举
        enum = enums[0]
        assert isinstance(enum, IREnum)
        assert enum.name == "Status"
        assert enum.typedef_alias == "Status"

    def test_parse_enum_values_with_explicit_values(self, parser):
        """测试解析带显式值的枚举"""
        code = """
typedef enum {
    STATUS_OK = 0,
    STATUS_ERROR = 1,
    STATUS_PENDING = 2
} Status;
"""
        result = parser.parse(code, "test.c")
        enums = result.get("enums", [])

        assert len(enums) == 1
        enum = enums[0]

        assert len(enum.values) == 3
        assert enum.values[0].name == "STATUS_OK"
        assert enum.values[0].value == 0
        assert enum.values[1].name == "STATUS_ERROR"
        assert enum.values[1].value == 1
        assert enum.values[2].name == "STATUS_PENDING"
        assert enum.values[2].value == 2

    def test_parse_enum_values_implicit_increment(self, parser):
        """测试解析隐式递增的枚举值"""
        code = """
typedef enum {
    TYPE_BUY,
    TYPE_SELL
} OrderType;
"""
        result = parser.parse(code, "test.c")
        enums = result.get("enums", [])

        assert len(enums) == 1
        enum = enums[0]

        assert len(enum.values) == 2
        assert enum.values[0].name == "TYPE_BUY"
        assert enum.values[0].value == 0
        assert enum.values[1].name == "TYPE_SELL"
        assert enum.values[1].value == 1

    def test_parse_enum_values_mixed(self, parser):
        """测试解析混合枚举值"""
        code = """
typedef enum {
    FIRST = 5,
    SECOND,
    THIRD = 10,
    FOURTH
} MyEnum;
"""
        result = parser.parse(code, "test.c")
        enums = result.get("enums", [])

        assert len(enums) == 1
        enum = enums[0]

        assert enum.values[0].value == 5
        assert enum.values[1].value == 6  # 自动递增
        assert enum.values[2].value == 10
        assert enum.values[3].value == 11  # 自动递增

    def test_parse_enum_values_helper(self, parser):
        """测试枚举值解析辅助方法"""
        body = """
    VALUE_A = 0,
    VALUE_B = 1,
    VALUE_C
"""
        values = parser._parse_enum_values(body)

        assert len(values) == 3
        assert values[0].name == "VALUE_A"
        assert values[0].value == 0
        assert values[2].name == "VALUE_C"
        assert values[2].value == 2  # 自动递增


# =============================================================================
# 文件解析测试
# =============================================================================

class TestParseFile:
    """文件解析测试"""

    def test_parse_file(self, parser, sample_c_file):
        """测试解析单个文件"""
        result = parser.parse_file(str(sample_c_file))

        assert "functions" in result
        assert "structs" in result
        assert len(result["functions"]) >= 1
        assert len(result["structs"]) >= 1

    def test_parse_nonexistent_file(self, parser):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError) as exc_info:
            parser.parse_file("nonexistent_file.c")

        assert "File not found" in str(exc_info.value)

    def test_parse_directory(self, parser, sample_c_dir):
        """测试解析目录"""
        result = parser.parse_directory(str(sample_c_dir))

        assert "functions" in result
        assert "files_processed" in result
        assert result["files_processed"] == 2
        assert len(result["functions"]) == 2

    def test_parse_nonexistent_directory(self, parser):
        """测试解析不存在的目录"""
        with pytest.raises(FileNotFoundError) as exc_info:
            parser.parse_directory("nonexistent_dir")

        assert "Directory not found" in str(exc_info.value)


# =============================================================================
# 完整解析测试 (集成测试)
# =============================================================================

class TestFullParse:
    """完整解析测试"""

    def test_parse_returns_all_types(self, parser):
        """测试解析返回所有类型"""
        code = """
typedef enum { A, B } MyEnum;

typedef struct {
    int x;
} MyStruct;

int my_func(int a) {
    return a;
}
"""
        result = parser.parse(code, "test.c")

        assert "functions" in result
        assert "structs" in result
        assert "enums" in result
        assert "file_path" in result

        assert len(result["functions"]) == 1
        assert len(result["structs"]) == 1
        assert len(result["enums"]) == 1

    def test_parse_empty_code(self, parser):
        """测试解析空代码"""
        result = parser.parse("", "empty.c")

        assert len(result["functions"]) == 0
        assert len(result["structs"]) == 0
        assert len(result["enums"]) == 0

    def test_parse_comments_only(self, parser):
        """测试解析只有注释的代码"""
        code = """
// 这是注释
/* 这也是注释 */
"""
        result = parser.parse(code, "comments.c")

        assert len(result["functions"]) == 0
        assert len(result["structs"]) == 0
        assert len(result["enums"]) == 0


# =============================================================================
# IRFunction 模型测试
# =============================================================================

class TestIRFunctionModel:
    """IRFunction 数据模型测试"""

    def test_create_ir_function(self):
        """测试创建 IRFunction"""
        func = IRFunction(
            name="test",
            file_path="test.c",
            line_number=1,
            return_type="int"
        )

        assert func.name == "test"
        assert func.file_path == "test.c"
        assert func.line_number == 1
        assert func.return_type == "int"
        assert func.is_static is False
        assert func.is_inline is False

    def test_ir_function_to_dict(self):
        """测试 IRFunction 序列化"""
        func = IRFunction(
            name="add",
            file_path="math.c",
            line_number=5,
            return_type="int",
            parameters=[
                IRParameter(name="a", type="int"),
                IRParameter(name="b", type="int"),
            ]
        )

        data = func.model_dump()
        assert data["name"] == "add"
        assert len(data["parameters"]) == 2


# =============================================================================
# IRStruct 模型测试
# =============================================================================

class TestIRStructModel:
    """IRStruct 数据模型测试"""

    def test_create_ir_struct(self):
        """测试创建 IRStruct"""
        struct = IRStruct(
            name="Point",
            file_path="geometry.c",
            line_number=10,
            fields=[
                IRField(name="x", type="int"),
                IRField(name="y", type="int"),
            ],
            typedef_alias="Point"
        )

        assert struct.name == "Point"
        assert len(struct.fields) == 2
        assert struct.typedef_alias == "Point"


# =============================================================================
# IREnum 模型测试
# =============================================================================

class TestIREnumModel:
    """IREnum 数据模型测试"""

    def test_create_irenum(self):
        """测试创建 IREnum"""
        enum = IREnum(
            name="Status",
            file_path="types.h",
            line_number=5,
            values=[
                IREnumValue(name="OK", value=0),
                IREnumValue(name="ERROR", value=1),
            ],
            typedef_alias="Status"
        )

        assert enum.name == "Status"
        assert len(enum.values) == 2
        assert enum.values[0].value == 0
