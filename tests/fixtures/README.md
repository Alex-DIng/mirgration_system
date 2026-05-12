# 测试夹具目录 - Test Fixtures

本目录包含测试用的各种夹具数据和样例文件。

## 目录结构

```
fixtures/
├── c_source/           # C 语言源码样例
│   ├── simple_function.c      # 简单函数样例
│   ├── order_struct.c         # 证券订单结构体样例
│   ├── function_pointer.c     # 函数指针样例
│   └── recursive_function.c   # 递归函数样例
│
├── java_expected/      # 预期的 Java 输出样例
│   ├── SimpleFunctionSample.java
│   └── SecuritiesOrder.java
│
├── ir/                 # IR 中间表示样例 (JSON 格式)
│   └── sample_order_ir.json
│
├── mocks/              # Mock 数据和响应
│   └── llm_responses.json
│
└── README.md           # 本说明文件
```

## 各目录用途

### c_source/
存放待迁移的 C 语言源码样例，用于：
- 测试 C 语言解析器的各项功能
- 验证调用图分析的正确性
- 端到端集成测试的输入

### java_expected/
存放预期的 Java 输出样例，用于：
- 对比生成代码的正确性
- 验证 Spring 注解使用是否恰当
- 作为代码生成的参考模板

### ir/
存放 IR（中间表示）的 JSON 样例，用于：
- 测试 IR 序列化/反序列化
- 离线分析和调试
- 作为数据交换格式

### mocks/
存放 Mock 数据，用于：
- LLM 客户端单元测试
- 模拟 API 响应
- 测试错误处理

## 添加新的测试夹具

1. 在相应目录下创建新文件
2. 在文件顶部添加注释说明用途
3. 在 `conftest.py` 中添加对应的 fixture（如需要）
4. 更新本说明文件

## 夹具使用示例

```python
# 在测试中使用夹具
from tests.conftest import sample_c_function

def test_parse_function(sample_c_function):
    parser = CParser()
    result = parser.parse(sample_c_function)
    assert len(result.functions) == 1
```
