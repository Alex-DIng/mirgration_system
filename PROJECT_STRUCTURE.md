# PROJECT_STRUCTURE.md — 目录结构与用途说明

## 项目概述

本项目利用**私有大语言模型（Private LLM）**，将一个大型 C 语言证券交易系统**自动化迁移**为基于 **Spring 框架的 Java 项目**。核心思路是：解析 C 源码 → 构建中间表示（IR）→ LLM 辅助理解业务语义 → 生成符合 Spring 规范的 Java 代码。

---

## 迁移流水线（5 个阶段）

```
C 源码  →  解析  →  分析  →  翻译(LLM)  →  生成  →  Java 代码
  │          │        │         │           │
  │     parser/   analyzer/   llm/     generator/
  │     core/ir   core/models core/models
  │
  knowledge/  （证券领域知识库全程辅助）
```

---

## 目录结构详解

### `src/` — 项目主源码

| 目录 | 用途 |
|---|---|
| `src/cli/` | **命令行入口**。提供 `migrate`、`parse`、`analyze`、`generate` 等子命令，是用户交互的唯一入口 |
| `src/core/` | **核心引擎**。包含迁移流水线的编排逻辑（`pipeline/`）和通用数据模型定义（`models/`），如 IR 节点类型、迁移任务状态等 |
| `src/core/pipeline/` | **流水线编排器**。按阶段（解析→分析→翻译→生成）串联各模块，管理任务调度、断点续传和增量迁移 |
| `src/core/models/` | **通用数据模型**。定义整个系统共用的 Pydantic 模型，如 `MigrationTask`、`FileMapping`、`TypeMapping`、`MigrationReport` 等 |
| `src/parser/` | **C 源码解析层**。负责将 C 代码解析为 AST，并转换为系统统一的中间表示（IR） |
| `src/parser/c_parser/` | **C 语言解析器**。基于 tree-sitter 实现 C 语法解析，提取函数、结构体、宏、全局变量、头文件依赖等 |
| `src/parser/ir/` | **中间表示（IR）定义**。定义与语言无关的中间表示结构，供后续分析和生成阶段使用。包含 `IRFunction`、`IRStruct`、`IRType`、`IRCall` 等 |
| `src/analyzer/` | **静态分析层**。对 IR 进行多维度分析，提取后续 LLM 翻译所需的结构化信息 |
| `src/analyzer/call_graph/` | **调用图分析**。构建函数调用关系图，识别调用链、递归、间接调用（函数指针）等 |
| `src/analyzer/data_flow/` | **数据流分析**。追踪关键数据（订单、行情、持仓等）在各函数间的流动路径 |
| `src/analyzer/dependency/` | **依赖分析**。分析 C 源文件间的 `#include` 依赖、全局变量依赖，确定迁移批次和顺序 |
| `src/generator/` | **Java 代码生成层**。将 LLM 翻译结果具体化为符合 Spring 框架规范的 Java 源文件 |
| `src/generator/java_writer/` | **Java 代码写入器**。负责拼装 package、import、类注解、方法体，并写出 `.java` 文件 |
| `src/generator/templates/` | **Jinja2 代码模板**。存放 Controller、Service、Repository、Entity、DTO、Config 等 Spring 组件的代码模板 |
| `src/llm/` | **私有大模型集成层**。封装对私有 LLM API 的调用，管理提示词和上下文 |
| `src/llm/client/` | **LLM 客户端适配器**。封装 OpenAI 兼容 API 调用，支持重试、流式输出、速率控制。可切换不同的后端模型 |
| `src/llm/prompts/` | **提示词模板管理**。用 Jinja2 管理各类提示词模板，支持动态填充 C 代码片段和分析上下文 |
| `src/llm/context/` | **上下文窗口管理**。将长 C 函数/文件分块，管理 token 预算，维护翻译过程中的上下文连贯性 |
| `src/knowledge/` | **领域知识库**。硬编码或检索增强的知识，减少 LLM 幻觉，确保翻译正确性 |
| `src/knowledge/securities/` | **证券领域知识**。涵盖证券业务规则、交易规则（连续竞价、集合竞价）、订单类型、风控逻辑等在 C 代码中常见的模式及其在 Java 中的对应表达 |
| `src/knowledge/spring/` | **Spring 框架知识**。Spring Bean 生命周期、事务管理 (`@Transactional`)、JPA 映射、AOP 切面、Spring Security 等最佳实践知识 |
| `src/utils/` | **工具函数库**。日志、文件 I/O、字符串处理、进度条、哈希校验等通用工具 |

---

### `tests/` — 测试套件

| 目录 | 用途 |
|---|---|
| `tests/unit/` | **单元测试**。覆盖解析器、分析器、生成器、LLM 客户端等各模块的独立测试 |
| `tests/integration/` | **集成测试**。测试完整流水线（parse→analyze→translate→generate）的端到端行为 |
| `tests/fixtures/` | **测试夹具**。存放测试用的 C 代码样例、预期的 Java 输出、mock LLM 响应等 |

---

### `data/` — 数据目录（不进入版本控制的核心产出）

| 目录 | 用途 |
|---|---|
| `data/input/c_source/` | **待迁移的原始 C 源码**。将证券交易系统的 `.c` / `.h` 文件按模块放入此处 |
| `data/output/java_source/` | **生成的 Java 源码**。迁移后产出的 Spring 项目 Java 文件，按 Maven 标准目录结构组织 |
| `data/intermediate/` | **中间产物**。存放解析产出的 IR JSON、分析报告（调用图、数据流图）等过程文件，便于断点续传和调试 |
| `data/mappings/` | **映射文件**。记录 C 符号 → Java 符号的对应关系（函数名、结构体名、全局变量名），供增量迁移和人工审核使用 |

---

### `config/` — 配置文件

存放 LLM 连接配置（endpoint、token、模型名）、迁移策略配置（分批规则、忽略清单）、日志级别等 YAML 配置文件。

---

### `scripts/` — 辅助脚本

批处理 C 文件预处理（如宏展开、注释清理）、结果验证（编译检查 Java 产出）、统计迁移覆盖率等一次性或运维脚本。

---

### `prompts/` — 提示词库（人工精调）

| 目录 | 用途 |
|---|---|
| `prompts/c_to_java/` | **C→Java 翻译提示词**。按场景分类：函数翻译、结构体→Entity 映射、指针→引用翻译、全局变量→Bean 注入等 |
| `prompts/spring_migration/` | **Spring 改造提示词**。指导 LLM 将直译的 Java 代码重构为符合 Spring 惯用法的代码 |

---

### `docs/` — 项目文档

架构设计、模块接口约定、LLM 提示词调优记录、迁移经验沉淀等文档。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 LLM 连接
cp config/llm.example.yaml config/llm.yaml
# 编辑 config/llm.yaml 填入私有模型的 endpoint 和 token

# 3. 放入待迁移的 C 源码
cp -r /path/to/c_project/* data/input/c_source/

# 4. 执行迁移（示例命令，待实现）
python -m src.cli migrate --source data/input/c_source --output data/output/java_source
```

---

## 设计原则

1. **阶段解耦**：解析→分析→翻译→生成四个阶段各司其职，中间通过 IR JSON 传递数据，任一阶段可独立重跑
2. **LLM 辅助而非替代**：LLM 负责语义理解和代码生成，结构化分析（调用图、数据流）走传统静态分析，互不依赖
3. **领域知识优先**：证券业务名词、风控规则等通过 `knowledge/` 目录硬编码注入，减少 LLM 幻觉
4. **增量可追溯**：每次 LLM 调用的输入/输出落盘到 `data/intermediate/`，映射关系记录到 `data/mappings/`，支持人工审计
