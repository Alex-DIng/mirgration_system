# mirgration_system

利用私有大语言模型（Private LLM），将大型 C 语言证券交易系统自动化迁移为 Spring 框架 Java 项目。

## 工作流

```
C 源码 → 解析(AST/IR) → 静态分析 → LLM 翻译 → Java 代码生成 → Spring 项目
```

各目录用途详见 [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)。

# prompts

我需要在mirgration_system下创建一个利用私有大模型的python的项目，这个项目是要将一个大型c的证券项目转化成使用spring框架的Java项目。现在我需要你先为这个项目生成必要的文件目录，并在更目录生成一个md文件来说明每个目录是为了什么目的而建的。
