# src 模块文档

## 目录结构

```
src/
├── __init__.py              # 包初始化，版本信息
├── README.md                # 本说明文档
│
├── cli/                     # 命令行接口
│   ├── __init__.py
│   └── main.py              # CLI 主程序
│
├── core/                    # 核心引擎
│   ├── __init__.py
│   ├── models/              # 数据模型
│   │   └── __init__.py      # Pydantic 模型定义
│   └── pipeline/            # 流水线编排
│       ├── __init__.py
│       └── pipeline.py      # MigrationPipeline
│
├── parser/                  # C 语言解析器
│   ├── __init__.py
│   ├── c_parser/            # C 解析器实现
│   │   ├── __init__.py
│   │   ├── parser.py        # CParser 类
│   │   └── ast_builder.py   # AST 构建器
│   └── ir/                  # 中间表示
│       └── __init__.py      # IR 数据类导出
│
├── analyzer/                # 静态分析器
│   ├── __init__.py
│   ├── call_graph/          # 调用图分析
│   │   ├── __init__.py
│   │   ├── call_graph.py    # CallGraph 类
│   │   └── analyzer.py      # CallGraphAnalyzer 类
│   ├── data_flow/           # 数据流分析
│   │   ├── __init__.py
│   │   └── analyzer.py      # DataFlowAnalyzer 类
│   └── dependency/          # 依赖分析
│       ├── __init__.py
│       └── analyzer.py      # DependencyAnalyzer 类
│
├── generator/               # Java 代码生成器
│   ├── __init__.py
│   ├── java_writer/         # Java 写入器
│   │   ├── __init__.py
│   │   └── writer.py        # JavaWriter 类
│   └── templates/           # 代码模板
│       ├── __init__.py
│       └── template_manager.py
│
├── llm/                     # 大语言模型集成
│   ├── __init__.py
│   ├── client/              # API 客户端
│   │   ├── __init__.py
│   │   └── client.py        # LLMClient 类
│   ├── context/             # 上下文管理
│   │   ├── __init__.py
│   │   └── context.py       # ContextManager 类
│   └── prompts/             # 提示词模板
│       ├── __init__.py
│       └── templates.py     # PromptTemplate 类
│
├── knowledge/               # 领域知识库
│   ├── __init__.py
│   ├── securities/          # 证券领域知识
│   │   ├── __init__.py
│   │   └── domain.py        # SecuritiesKnowledge 类
│   └── spring/              # Spring 框架知识
│       ├── __init__.py
│       └── domain.py        # SpringKnowledge 类
│
└── utils/                   # 工具函数
    ├── __init__.py
    ├── logger.py            # 日志配置
    ├── file_io.py           # 文件 I/O
    ├── string_utils.py      # 字符串处理
    └── token_utils.py       # Token 计数
```

## 模块说明

### cli/ - 命令行接口

提供迁移系统的命令行入口。

```bash
# 执行完整迁移
python -m src.cli migrate --source ./c_source --output ./java_output

# 仅解析 C 源码
python -m src.cli parse --source ./c_source --output ./ir.json

# 仅执行分析
python -m src.cli analyze --source ./c_source --output ./analysis.json

# 配置管理
python -m src.cli config init
```

### core/ - 核心引擎

**models/**: 定义整个系统共用的 Pydantic 数据模型：
- `MigrationConfig`: 迁移任务配置
- `MigrationReport`: 迁移报告
- `IRFunction`, `IRStruct`, `IREnum`: IR 数据模型
- `FileMapping`, `TypeMapping`: 映射关系

**pipeline/**: 迁移流水线编排器 `MigrationPipeline`：
1. 解析阶段：C 源码 → IR
2. 分析阶段：构建调用图、数据流分析
3. 翻译阶段：LLM 辅助语义翻译
4. 生成阶段：生成 Spring Java 代码

### parser/ - C 语言解析器

**c_parser/**: C 语言解析器，基于 tree-sitter：
- 解析函数定义、结构体、枚举
- 提取函数调用关系
- 识别头文件依赖

**ir/**: 中间表示定义，供后续阶段使用。

### analyzer/ - 静态分析器

**call_graph/**: 调用图分析
- 构建函数调用关系图
- 检测直接/间接递归
- 识别调用链和入口函数

**data_flow/**: 数据流分析
- 追踪关键数据的流动路径
- 识别数据的创建、修改、销毁

**dependency/**: 依赖分析
- 分析文件间依赖关系
- 生成推荐迁移顺序

### generator/ - Java 代码生成器

**java_writer/**: Java 代码写入器
- 生成 Entity 类 (带 JPA 注解)
- 生成 Repository 接口
- 生成 Service 类
- 生成 Controller 类

**templates/**: Jinja2 代码模板管理

### llm/ - 大语言模型集成

**client/**: LLM API 客户端
- 封装 OpenAI 兼容 API
- 支持自动重试
- 流式输出

**context/**: 上下文窗口管理
- Token 计数
- 上下文截断
- 保存/加载

**prompts/**: 提示词模板管理
- C 到 Java 翻译模板
- 带上下文的翻译模板

### knowledge/ - 领域知识库

**securities/**: 证券领域知识
- 订单类型 (买入/卖出)
- 订单状态 (待报/已报/成交/撤单/废单)
- 业务规则验证

**spring/**: Spring 框架知识
- 核心注解 (@Component, @Service, @Repository, @Controller)
- JPA 注解 (@Entity, @Table, @Id, @Column)
- 事务管理 (@Transactional)
- 代码规范验证

### utils/ - 工具函数

- **logger**: 日志配置
- **file_io**: 文件读写、文件查找
- **string_utils**: 命名转换 (camelCase, snake_case, PascalCase)
- **token_utils**: Token 计数和成本估算

## 使用示例

### 基本用法

```python
from src.core.models import MigrationConfig, LLMConfig
from src.core.pipeline import MigrationPipeline

# 配置
llm_config = LLMConfig(
    endpoint="http://localhost:8080/v1",
    api_key="your-api-key",
    model="private-llm"
)

config = MigrationConfig(
    source_dir="data/input/c_source",
    output_dir="data/output/java_source",
    llm=llm_config
)

# 执行迁移
pipeline = MigrationPipeline(config)
report = pipeline.run()

print(f"迁移完成：{report.files_processed} 个文件")
```

### 单独使用各模块

```python
# 解析 C 源码
from src.parser.c_parser import CParser

parser = CParser()
result = parser.parse_file("example.c")
print(f"Found {len(result['functions'])} functions")

# 调用图分析
from src.analyzer.call_graph import CallGraphAnalyzer

analyzer = CallGraphAnalyzer()
graph = analyzer.build_from_ir(result['functions'])
report = analyzer.analyze()
print(f"Recursive functions: {report['recursive_functions']}")

# Java 代码生成
from src.generator.java_writer import JavaWriter

writer = JavaWriter(output_dir="./output")
writer.generate_entity({
    "class_name": "Order",
    "fields": [...]
})
```

## 依赖

- Python 3.9+
- pydantic: 数据验证
- tree-sitter: C 语言解析 (可选)
- jinja2: 模板渲染
- requests: HTTP 请求

## 设计原则

1. **阶段解耦**: 解析→分析→翻译→生成四阶段独立，通过 IR 传递数据
2. **LLM 辅助**: LLM 负责语义理解，传统分析负责结构化信息
3. **领域知识优先**: 证券业务知识硬编码，减少 LLM 幻觉
4. **增量可追溯**: 映射关系记录，支持人工审计
