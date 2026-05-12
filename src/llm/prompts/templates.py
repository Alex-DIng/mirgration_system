"""
提示词模板 - Prompt Templates

定义和管理用于 C 到 Java 翻译的提示词模板。
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptTemplate:
    """
    提示词模板

    支持简单的变量替换语法：{{ variable_name }}

    示例:
        template = PromptTemplate("Translate {{ c_code }} to Java")
        result = template.render(c_code="int add(...) {...}")
    """

    def __init__(self, template: str, name: Optional[str] = None):
        """
        初始化模板

        Args:
            template: 模板字符串
            name: 模板名称
        """
        self.template = template
        self.name = name

    def render(self, **kwargs) -> str:
        """
        渲染模板

        Args:
            **kwargs: 变量替换值

        Returns:
            渲染后的文本
        """
        result = self.template
        for key, value in kwargs.items():
            if isinstance(value, str):
                result = result.replace(f"{{{{ {key} }}}}", value)
            elif isinstance(value, (list, dict)):
                result = result.replace(f"{{{{ {key} }}}}", str(value))
        return result

    @classmethod
    def from_file(cls, file_path: str) -> "PromptTemplate":
        """
        从文件加载模板

        Args:
            file_path: 文件路径

        Returns:
            PromptTemplate 实例
        """
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return cls(template=content, name=path.stem)


class PromptTemplateManager:
    """
    提示词模板管理器

    预定义常用的 C 到 Java 翻译提示词模板。
    """

    # 预定义模板
    TEMPLATES = {
        "c_to_java_function": """
你是一个专业的 C 到 Java 代码迁移助手。
请将以下 C 语言函数翻译为 Java 代码。

要求:
1. 保持原有的业务逻辑
2. 使用 Java 命名规范
3. 添加必要的 JavaDoc 注释
4. 处理指针到引用的转换

C 代码:
```c
{{ c_code }}
```

请生成对应的 Java 代码:
""".strip(),

        "c_to_java_struct": """
你是一个专业的 C 到 Java 代码迁移助手。
请将以下 C 语言结构体转换为 Java Entity 类。

要求:
1. 使用 JPA 注解 (@Entity, @Table, @Column)
2. 使用 Lombok 简化代码 (@Data)
3. 保持字段类型对应
4. 添加必要的 JavaDoc

C 结构体:
```c
{{ c_struct }}
```

请生成对应的 Java Entity 类:
""".strip(),

        "c_to_java_with_context": """
你是一个专业的 C 到 Java 代码迁移助手。
请根据提供的上下文信息，将 C 代码翻译为 Java。

调用图上下文:
{{ call_graph }}

数据流上下文:
{{ data_flow }}

领域知识:
{{ domain_knowledge }}

C 代码:
```c
{{ c_code }}
```

请生成符合 Spring 框架规范的 Java 代码:
""".strip(),

        "spring_service_generation": """
请为以下 Java Entity 类生成对应的 Service 类。

Entity 类:
{{ entity_code }}

要求:
1. 使用 @Service 注解
2. 使用 @Transactional 管理事务
3. 注入 Repository
4. 实现基本的 CRUD 方法

请生成 Service 类代码:
""".strip(),

        "spring_controller_generation": """
请为以下 Service 类生成对应的 REST Controller。

Service:
{{ service_code }}

Entity:
{{ entity_code }}

要求:
1. 使用 @RestController
2. 使用 @RequestMapping 定义路由
3. 实现 GET/POST/PUT/DELETE 端点
4. 使用 ResponseEntity 包装返回值

请生成 Controller 类代码:
""".strip(),

        "code_review": """
请审查以下生成的 Java 代码，指出可能的问题:

{{ java_code }}

请检查:
1. 是否有编译错误
2. 是否有潜在的运行时错误
3. 是否符合 Spring 最佳实践
4. 是否有性能问题

请提供具体的改进建议:
""".strip(),
    }

    def __init__(self):
        """初始化模板管理器"""
        self._templates: Dict[str, PromptTemplate] = {}

        # 加载预定义模板
        for name, content in self.TEMPLATES.items():
            self._templates[name] = PromptTemplate(template=content, name=name)

    def get(self, name: str) -> Optional[PromptTemplate]:
        """
        获取模板

        Args:
            name: 模板名称

        Returns:
            PromptTemplate 或 None
        """
        return self._templates.get(name)

    def render(self, name: str, **kwargs) -> str:
        """
        渲染模板

        Args:
            name: 模板名称
            **kwargs: 渲染变量

        Returns:
            渲染后的文本
        """
        template = self.get(name)
        if template is None:
            raise ValueError(f"Template not found: {name}")
        return template.render(**kwargs)

    def register(self, name: str, template: str) -> None:
        """
        注册自定义模板

        Args:
            name: 模板名称
            template: 模板字符串
        """
        self._templates[name] = PromptTemplate(template=template, name=name)
        logger.info(f"Template registered: {name}")

    def list_templates(self) -> list:
        """列出所有可用模板"""
        return list(self._templates.keys())


# 全局实例
_default_manager = PromptTemplateManager()


def get_template(name: str) -> Optional[PromptTemplate]:
    """获取全局模板"""
    return _default_manager.get(name)


def render_template(name: str, **kwargs) -> str:
    """渲染全局模板"""
    return _default_manager.render(name, **kwargs)
