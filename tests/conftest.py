"""
Pytest 共享配置和 Fixtures

本文件定义全局可用的测试夹具和配置。
"""

import pytest
from pathlib import Path


# =============================================================================
# 路径 Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def tests_root() -> Path:
    """测试目录根路径"""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def fixtures_dir(tests_root: Path) -> Path:
    """测试夹具目录"""
    return tests_root / "fixtures"


@pytest.fixture(scope="session")
def c_source_fixtures(fixtures_dir: Path) -> Path:
    """C 源码夹具目录"""
    return fixtures_dir / "c_source"


@pytest.fixture(scope="session")
def java_expected_fixtures(fixtures_dir: Path) -> Path:
    """预期 Java 输出夹具目录"""
    return fixtures_dir / "java_expected"


@pytest.fixture(scope="session")
def ir_fixtures(fixtures_dir: Path) -> Path:
    """IR 中间表示夹具目录"""
    return fixtures_dir / "ir"


# =============================================================================
# 临时目录 Fixtures
# =============================================================================

@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """
    临时输出目录

    每个测试用例独立的临时目录，测试结束后自动清理。
    """
    output = tmp_path / "output"
    output.mkdir(parents=True, exist_ok=True)
    return output


@pytest.fixture
def temp_ir_dir(tmp_path: Path) -> Path:
    """
    临时 IR 存储目录

    用于测试中间表示的序列化/反序列化。
    """
    ir_dir = tmp_path / "ir"
    ir_dir.mkdir(parents=True, exist_ok=True)
    return ir_dir


# =============================================================================
# 测试数据 Fixtures
# =============================================================================

@pytest.fixture
def sample_c_function() -> str:
    """简单的 C 函数样例"""
    return """
int add(int a, int b) {
    return a + b;
}
"""


@pytest.fixture
def sample_c_struct() -> str:
    """C 结构体样例"""
    return """
typedef struct {
    int order_id;
    char symbol[32];
    int quantity;
    double price;
} Order;
"""


@pytest.fixture
def sample_c_with_calls() -> str:
    """包含函数调用的 C 代码样例"""
    return """
void log_message(const char* msg) {
    printf("%s\\n", msg);
}

int process_order(Order* order) {
    log_message("Processing order");
    if (validate_order(order)) {
        return execute_order(order);
    }
    return -1;
}

int validate_order(Order* order) {
    return order->quantity > 0;
}

int execute_order(Order* order) {
    log_message("Executing order");
    return 0;
}
"""


@pytest.fixture
def sample_c_recursive() -> str:
    """递归函数 C 代码样例"""
    return """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
"""


@pytest.fixture
def sample_c_function_pointer() -> str:
    """包含函数指针的 C 代码样例"""
    return """
typedef int (*CompareFunc)(const void*, const void*);

int compare_int(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

void sort_array(int* arr, int size, CompareFunc cmp) {
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            if (cmp(&arr[j], &arr[j+1]) > 0) {
                int tmp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = tmp;
            }
        }
    }
}
"""


@pytest.fixture
def sample_c_security_order() -> str:
    """证券订单相关 C 代码样例（贴近实际业务）"""
    return """
typedef enum {
    ORDER_TYPE_BUY,
    ORDER_TYPE_SELL
} OrderType;

typedef struct {
    int order_id;
    OrderType type;
    char stock_code[16];
    int quantity;
    double price;
    int status;
} SecuritiesOrder;

int submit_order(SecuritiesOrder* order) {
    if (!validate_order_params(order)) {
        return ERR_INVALID_PARAMS;
    }
    if (!check_risk_limit(order)) {
        return ERR_RISK_LIMIT_EXCEEDED;
    }
    return send_to_exchange(order);
}

int validate_order_params(SecuritiesOrder* order) {
    if (order->quantity <= 0) {
        return 0;
    }
    if (order->price < 0.0) {
        return 0;
    }
    return 1;
}

int check_risk_limit(SecuritiesOrder* order) {
    // 风控检查逻辑
    return 1;
}

int send_to_exchange(SecuritiesOrder* order) {
    // 发送到交易所
    return 0;
}
"""


# =============================================================================
# IR 数据 Fixtures
# =============================================================================

@pytest.fixture
def sample_ir_function() -> dict:
    """IR 函数样例"""
    return {
        "name": "add",
        "file_path": "test.c",
        "line_number": 1,
        "return_type": "int",
        "parameters": [
            {"name": "a", "type": "int"},
            {"name": "b", "type": "int"}
        ],
        "calls": [],
        "body": "return a + b;"
    }


@pytest.fixture
def sample_ir_with_calls() -> list:
    """包含调用关系的 IR 函数列表样例"""
    return [
        {
            "name": "log_message",
            "file_path": "utils.c",
            "line_number": 5,
            "return_type": "void",
            "parameters": [{"name": "msg", "type": "const char*"}],
            "calls": [{"name": "printf", "line": 6, "type": "direct"}],
        },
        {
            "name": "validate_order",
            "file_path": "order.c",
            "line_number": 10,
            "return_type": "int",
            "parameters": [{"name": "order", "type": "Order*"}],
            "calls": [],
        },
        {
            "name": "execute_order",
            "file_path": "order.c",
            "line_number": 20,
            "return_type": "int",
            "parameters": [{"name": "order", "type": "Order*"}],
            "calls": [{"name": "log_message", "line": 21, "type": "direct"}],
        },
        {
            "name": "process_order",
            "file_path": "order.c",
            "line_number": 1,
            "return_type": "int",
            "parameters": [{"name": "order", "type": "Order*"}],
            "calls": [
                {"name": "log_message", "line": 2, "type": "direct"},
                {"name": "validate_order", "line": 3, "type": "direct"},
                {"name": "execute_order", "line": 4, "type": "direct"},
            ],
        },
    ]


# =============================================================================
# Pytest 配置
# =============================================================================

def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试标记"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试标记"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试标记"
    )
