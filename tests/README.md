# 测试套件文档 - Test Suite Documentation

## 概述

本测试套件覆盖迁移系统的各个模块，包括单元测试、集成测试和性能测试。

## 目录结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # Pytest 共享配置和 Fixtures
├── README.md                # 测试套件文档（本文件）
│
├── fixtures/                # 测试夹具数据
│   ├── c_source/            # C 源码样例
│   ├── java_expected/       # 预期 Java 输出
│   ├── ir/                  # IR 中间表示样例
│   ├── mocks/               # Mock 数据
│   └── README.md            # 夹具说明
│
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── analyzer/            # 分析器测试
│   │   └── test_call_graph.py
│   ├── parser/              # 解析器测试
│   │   └── test_c_parser.py
│   ├── generator/           # 生成器测试
│   │   └── test_java_writer.py
│   └── llm/                 # LLM 测试
│       └── test_client.py
│
└── integration/             # 集成测试
    ├── __init__.py
    ├── test_pipeline.py     # 流水线端到端测试
    └── test_call_graph_integration.py  # 调用图集成测试
```

## 运行测试

### 基本命令

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/analyzer/test_call_graph.py

# 运行特定测试类
pytest tests/unit/analyzer/test_call_graph.py::TestCallGraph

# 运行特定测试函数
pytest tests/unit/analyzer/test_call_graph.py::TestCallGraph::test_add_node
```

### 带选项运行

```bash
# 详细输出
pytest -v

# 显示覆盖率
pytest --cov=src --cov-report=html

# 仅运行失败的测试
pytest --lf

# 运行标记的测试
pytest -m unit
pytest -m integration
pytest -m slow

# 跳过慢速测试
pytest -m "not slow"
```

### 生成覆盖率报告

```bash
# HTML 报告
pytest --cov=src --cov-report=html
# 打开 coverage_html_report/index.html

# 终端报告
pytest --cov=src --cov-report=term-missing

# XML 报告（用于 CI）
pytest --cov=src --cov-report=xml
```

## 测试分类

### 单元测试 (Unit Tests)
- 测试单个模块/类的功能
- 不依赖外部服务
- 快速执行
- 使用 `@pytest.mark.unit` 标记

### 集成测试 (Integration Tests)
- 测试多个模块的协同工作
- 可能需要文件系统或 Mock 服务
- 执行时间中等
- 使用 `@pytest.mark.integration` 标记

### 性能测试 (Performance Tests)
- 测试大量数据或复杂场景
- 执行时间较长
- 使用 `@pytest.mark.slow` 标记

## 编写新测试

### 测试文件命名
- 文件名：`test_<module>.py`
- 测试类：`Test<ClassName>`
- 测试函数：`test_<description>()`

### 测试模板

```python
"""
模块名单元测试 - Module Unit Tests

测试覆盖：
- 功能点 1
- 功能点 2
"""

import pytest
from src.module import MyClass


class TestMyClass:
    """MyClass 测试类"""

    def test_basic_functionality(self):
        """测试基本功能"""
        obj = MyClass()
        result = obj.do_something()
        assert result is not None

    def test_with_fixture(self, sample_data):
        """测试带夹具的数据"""
        obj = MyClass()
        result = obj.process(sample_data)
        assert result.expected == True
```

### 使用 Fixtures

在 `conftest.py` 中定义共享夹具：

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

@pytest.fixture
def temp_output_dir(tmp_path):
    return tmp_path / "output"
```

在测试中使用：

```python
def test_with_data(sample_data):
    assert sample_data["key"] == "value"

def test_with_temp_dir(temp_output_dir):
    (temp_output_dir / "test.txt").write_text("content")
    assert temp_output_dir.exists()
```

## 测试数据

### C 源码样例
位于 `fixtures/c_source/`，包含：
- 简单函数
- 结构体定义
- 函数指针
- 递归函数

### Java 预期输出
位于 `fixtures/java_expected/`，包含：
- 简单的 Java 类
- Spring Entity 类
- Repository 接口样例

### Mock 数据
位于 `fixtures/mocks/`，包含：
- LLM API 响应
- 错误响应样例

## CI/CD 集成

在 CI 环境中运行测试：

```yaml
# GitHub Actions 示例
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## 常见问题

### Q: 测试跳过怎么办？
A: 许多测试标记为 `@pytest.skip("模块尚未实现")`，当对应模块实现后移除跳过标记。

### Q: 如何调试失败的测试？
A: 使用 `-s` 选项显示 print 输出，使用 `--pdb` 进入调试模式：
```bash
pytest -s --pdb tests/...
```

### Q: 如何测试异步代码？
A: 使用 `pytest-asyncio` 插件：
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_func()
    assert result is not None
```

## 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
