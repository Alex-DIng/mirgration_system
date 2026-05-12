"""
模板管理器 - Template Manager

使用 Jinja2 管理代码生成模板。
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    模板管理器

    管理 Jinja2 代码模板，支持：
        - 模板加载和缓存
        - 模板渲染
        - 自定义过滤器
    """

    # 内联模板 (避免外部文件依赖)
    TEMPLATES = {
        "entity": """{% extends "base.java" %}
{% block content %}
@Entity
@Table(name = "{{ table_name }}")
@Data
@NoArgsConstructor
public class {{ class_name }} {
{% for field in fields %}
    {% if field.is_id %}
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    {% endif %}
    @Column(name = "{{ field.column }}")
    private {{ field.java_type }} {{ field.name }};
{% endfor %}
}
{% endblock %}
""",

        "repository": """package {{ package }}.repository;

import {{ package }}.entity.{{ entity_name }};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface {{ entity_name }}Repository extends JpaRepository<{{ entity_name }}, {{ id_type }}> {
}
""",

        "service": """package {{ package }}.service;

import {{ package }}.entity.{{ entity_name }};
import {{ package }}.repository.{{ entity_name }}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class {{ service_name }} {
    @Autowired
    private {{ entity_name }}Repository repository;
}
""",

        "controller": """package {{ package }}.controller;

import {{ package }}.entity.{{ entity_name }};
import {{ package }}.service.{{ service_name }};
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

@RestController
@RequestMapping("{{ route }}")
public class {{ controller_name }} {
    @Autowired
    private {{ service_name }} service;
}
""",

        "enum": """package {{ package }}.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum {{ enum_name }} {
{% for value in values %}
    {{ value.name }}({{ value.code }}){% if not loop.last %},{% endif %}
{% endfor %};

    private final int code;
}
""",
    }

    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化模板管理器

        Args:
            template_dir: 外部模板目录 (可选)
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self._cache: Dict[str, str] = {}
        self._setup_jinja()

    def _setup_jinja(self) -> None:
        """设置 Jinja2 环境"""
        try:
            from jinja2 import Environment, BaseLoader

            class DictLoader(BaseLoader):
                def __init__(self, templates):
                    self.templates = templates

                def get_source(self, environment, template):
                    if template in self.templates:
                        return self.templates[template], template, lambda: True
                    raise TemplateNotFound(template)

            self.env = Environment(loader=DictLoader(self.TEMPLATES))
            self._jinja_available = True
            logger.debug("Jinja2 initialized successfully")
        except ImportError:
            self.env = None
            self._jinja_available = False
            logger.warning("Jinja2 not available, using fallback rendering")

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染模板

        Args:
            template_name: 模板名
            context: 渲染上下文

        Returns:
            渲染后的代码
        """
        if self._jinja_available and self.env:
            try:
                template = self.env.get_template(template_name)
                return template.render(**context)
            except Exception as e:
                logger.warning(f"Jinja2 rendering failed: {e}, using fallback")

        # Fallback: 简单字符串替换
        return self._render_fallback(template_name, context)

    def _render_fallback(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """简单的字符串替换渲染"""
        template = self.TEMPLATES.get(template_name, "")

        # 简单替换 {{ key }} 为 value
        for key, value in context.items():
            if isinstance(value, str):
                template = template.replace(f"{{{{ {key} }}}}", value)
            elif isinstance(value, list) and key == "fields":
                # 处理字段列表
                field_code = ""
                for field in value:
                    field_code += f"    private {field.get('java_type', 'Object')} {field.get('name', 'unknown')};\n"
                template = template.replace("{{ fields }}", field_code)

        return template

    def get_template(self, template_name: str) -> Optional[str]:
        """获取模板内容"""
        return self.TEMPLATES.get(template_name)

    def register_template(self, name: str, content: str) -> None:
        """注册自定义模板"""
        self.TEMPLATES[name] = content
        if self.env:
            self.env.loader.templates[name] = content
        logger.info(f"Template registered: {name}")
