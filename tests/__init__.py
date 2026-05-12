"""
测试套件 - Migration System Test Suite

测试目录结构：
- fixtures/: 测试夹具（C 代码样例、预期 Java 输出、mock 数据）
- unit/: 单元测试（各模块独立测试）
- integration/: 集成测试（完整流水线端到端测试）

运行测试：
    pytest tests/                          # 运行所有测试
    pytest tests/unit/                     # 仅运行单元测试
    pytest tests/integration/              # 仅运行集成测试
    pytest tests/ -v                       # 详细输出
    pytest tests/ --cov=src                # 带覆盖率报告
"""
