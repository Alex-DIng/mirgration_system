"""
Java 代码写入器实现 - Java Writer Implementation
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class JavaWriter:
    """
    Java 代码写入器

    负责生成符合 Spring 规范的 Java 代码。

    功能:
        - 生成 Entity 类
        - 生成 Repository 接口
        - 生成 Service 类
        - 生成 Controller 类
        - 生成 Enum 枚举
    """

    def __init__(self, output_dir: str, package_prefix: str = "com.migration"):
        """
        初始化写入器

        Args:
            output_dir: 输出目录
            package_prefix: Java 包名前缀
        """
        self.output_dir = Path(output_dir)
        self.package_prefix = package_prefix
        self._generated_files: List[str] = []

        # 创建标准目录结构
        self._setup_directories()

    def _setup_directories(self) -> None:
        """创建标准 Maven/Gradle 目录结构"""
        base_dir = self.output_dir / "src" / "main" / "java"
        self.entity_dir = base_dir / self.package_prefix.replace(".", "/") / "entity"
        self.repository_dir = base_dir / self.package_prefix.replace(".", "/") / "repository"
        self.service_dir = base_dir / self.package_prefix.replace(".", "/") / "service"
        self.controller_dir = base_dir / self.package_prefix.replace(".", "/") / "controller"
        self.config_dir = base_dir / self.package_prefix.replace(".", "/") / "config"
        self.enums_dir = base_dir / self.package_prefix.replace(".", "/") / "enums"

        for dir_path in [
            self.entity_dir,
            self.repository_dir,
            self.service_dir,
            self.controller_dir,
            self.config_dir,
            self.enums_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Output directories created at {self.output_dir}")

    def generate_entity(self, entity_data: Dict[str, Any]) -> str:
        """
        生成 Entity 类

        Args:
            entity_data: 实体数据，包含 class_name, fields 等

        Returns:
            生成的文件路径
        """
        class_name = entity_data.get("class_name", "UnknownEntity")
        package = f"{self.package_prefix}.entity"

        code = self._generate_entity_code(entity_data, package)
        file_path = self.entity_dir / f"{class_name}.java"

        self._write_file(file_path, code)
        logger.info(f"Generated entity: {file_path}")
        return str(file_path)

    def _generate_entity_code(
        self,
        entity_data: Dict[str, Any],
        package: str
    ) -> str:
        """生成 Entity 类代码"""
        class_name = entity_data.get("class_name", "Entity")
        table_name = entity_data.get("table_name", self._to_snake_case(class_name))
        fields = entity_data.get("fields", [])
        imports = entity_data.get("imports", [])

        # 基础 import
        default_imports = [
            "jakarta.persistence.*",
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "lombok.AllArgsConstructor",
        ]

        # 检查是否有枚举字段
        has_enum = any(f.get("is_enum") for f in fields)
        if has_enum:
            default_imports.append("java.time.LocalDateTime")

        all_imports = list(set(default_imports + imports))

        # 生成代码
        code_lines = [
            f"package {package};",
            "",
        ]

        # Import 语句
        for imp in sorted(all_imports):
            code_lines.append(f"import {imp};")

        code_lines.extend([
            "",
            "/**",
            f" * {class_name} 实体类",
            " * 由迁移工具自动生成",
            " */",
            "@Entity",
            f"@Table(name = \"{table_name}\")",
            "@Data",
            "@NoArgsConstructor",
            f"public class {class_name} {{",
            "",
        ])

        # 字段
        for field in fields:
            code_lines.extend(self._generate_field_code(field))

        # 构造函数
        code_lines.extend(self._generate_constructors(class_name, fields))

        # Getter/Setter (使用 Lombok 时可省略)
        # code_lines.extend(self._generate_getters_setters(fields))

        # toString 方法
        code_lines.append(self._generate_to_string(class_name, fields))

        code_lines.append("}")

        return "\n".join(code_lines)

    def _generate_field_code(self, field: Dict[str, Any]) -> List[str]:
        """生成字段代码"""
        lines = []
        name = field.get("name", "unknown")
        java_type = field.get("java_type", "Object")
        column_name = field.get("column", self._to_snake_case(name))
        is_id = field.get("is_id", False)
        is_enum = field.get("is_enum", False)

        # 注解
        if is_id:
            lines.append("    @Id")
            lines.append("    @GeneratedValue(strategy = GenerationType.IDENTITY)")

        lines.append(f"    @Column(name = \"{column_name}\")")

        if is_enum:
            lines.append("    @Enumerated(EnumType.ORDINAL)")

        # 字段声明
        lines.append(f"    private {java_type} {name};")
        lines.append("")

        return lines

    def _generate_constructors(
        self,
        class_name: str,
        fields: List[Dict[str, Any]]
    ) -> List[str]:
        """生成构造函数"""
        lines = []

        # 全参构造函数
        if fields:
            params = ", ".join(
                f"{f['java_type']} {f['name']}" for f in fields
            )
            lines.append("    @AllArgsConstructor")
            lines.append("    public " + class_name + "(" + params + ") {")
            for field in fields:
                lines.append(f"        this.{field['name']} = {field['name']};")
            lines.append("    }")
            lines.append("")

        return lines

    def _generate_to_string(
        self,
        class_name: str,
        fields: List[Dict[str, Any]]
    ) -> str:
        """生成 toString 方法"""
        field_names = ", ".join(f"{f['name']}=" + f"{f['name']}" for f in fields)
        return f"""
    @Override
    public String toString() {{
        return "{class_name}[" + {field_names} + "]";
    }}"""

    def generate_repository(
        self,
        entity_name: str,
        id_type: str = "Long"
    ) -> str:
        """
        生成 Repository 接口

        Args:
            entity_name: 实体类名
            id_type: ID 类型

        Returns:
            生成的文件路径
        """
        package = f"{self.package_prefix}.repository"
        interface_name = f"{entity_name}Repository"

        code = f"""package {package};

import {self.package_prefix}.entity.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * {entity_name} Repository 接口
 * 由迁移工具自动生成
 */
@Repository
public interface {interface_name} extends JpaRepository<{entity_name}, {id_type}> {{

    // 可在此添加自定义查询方法
}}
"""
        file_path = self.repository_dir / f"{interface_name}.java"
        self._write_file(file_path, code)
        logger.info(f"Generated repository: {file_path}")
        return str(file_path)

    def generate_service(
        self,
        service_name: str,
        entity_name: str
    ) -> str:
        """
        生成 Service 类

        Args:
            service_name: 服务类名
            entity_name: 实体类名

        Returns:
            生成的文件路径
        """
        package = f"{self.package_prefix}.service"
        class_name = service_name

        code = f"""package {package};

import {self.package_prefix}.entity.{entity_name};
import {self.package_prefix}.repository.{entity_name}Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * {class_name} 服务类
 * 由迁移工具自动生成
 */
@Service
@Transactional
public class {class_name} {{

    @Autowired
    private {entity_name}Repository repository;

    public List<{entity_name}> findAll() {{
        return repository.findAll();
    }}

    public Optional<{entity_name}> findById({{id_type}} id) {{
        return repository.findById(id);
    }}

    public {entity_name} save({entity_name} entity) {{
        return repository.save(entity);
    }}

    public void deleteById(Long id) {{
        repository.deleteById(id);
    }}
}}
""".replace("{{id_type}}", "Long")

        file_path = self.service_dir / f"{class_name}.java"
        self._write_file(file_path, code)
        logger.info(f"Generated service: {file_path}")
        return str(file_path)

    def generate_controller(
        self,
        controller_name: str,
        entity_name: str,
        route_path: str
    ) -> str:
        """
        生成 Controller 类

        Args:
            controller_name: 控制器类名
            entity_name: 实体类名
            route_path: 路由路径

        Returns:
            生成的文件路径
        """
        package = f"{self.package_prefix}.controller"
        class_name = controller_name

        entity_var = entity_name[0].lower() + entity_name[1:]

        code = f"""package {package};

import {self.package_prefix}.entity.{entity_name};
import {self.package_prefix}.service.{class_name.replace('Controller', 'Service')};
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * {class_name} 控制器
 * 由迁移工具自动生成
 */
@RestController
@RequestMapping("{route_path}")
public class {class_name} {{

    @Autowired
    private {class_name.replace('Controller', 'Service')} service;

    @GetMapping
    public List<{entity_name}> getAll() {{
        return service.findAll();
    }}

    @GetMapping("/{{id}}")
    public {entity_name} getById(@PathVariable Long id) {{
        return service.findById(id).orElse(null);
    }}

    @PostMapping
    public {entity_name} create(@RequestBody {entity_name} {entity_var}) {{
        return service.save({entity_var});
    }}

    @DeleteMapping("/{{id}}")
    public void delete(@PathVariable Long id) {{
        service.deleteById(id);
    }}
}}
"""
        file_path = self.controller_dir / f"{class_name}.java"
        self._write_file(file_path, code)
        logger.info(f"Generated controller: {file_path}")
        return str(file_path)

    def generate_enum(self, enum_data: Dict[str, Any]) -> str:
        """
        生成 Enum 枚举

        Args:
            enum_data: 枚举数据，包含 name, values

        Returns:
            生成的文件路径
        """
        package = f"{self.package_prefix}.enums"
        enum_name = enum_data.get("name", "UnknownEnum")
        values = enum_data.get("values", [])

        value_lines = []
        for i, val in enumerate(values):
            val_name = val.get("name", "UNKNOWN")
            val_code = val.get("value", i)
            value_lines.append(f"    {val_name}({val_code})")

        code = f"""package {package};

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * {enum_name} 枚举
 * 由迁移工具自动生成
 */
@Getter
@AllArgsConstructor
public enum {enum_name} {{

{',\n'.join(value_lines)};

    private final int code;

    public static {enum_name} fromCode(int code) {{
        for ({enum_name} e : values()) {{
            if (e.getCode() == code) {{
                return e;
            }}
        }}
        throw new IllegalArgumentException("Unknown code: " + code);
    }}
}}
"""
        file_path = self.enums_dir / f"{enum_name}.java"
        self._write_file(file_path, code)
        logger.info(f"Generated enum: {file_path}")
        return str(file_path)

    def _write_file(self, file_path: Path, code: str) -> None:
        """写入文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        self._generated_files.append(str(file_path))

    def _to_snake_case(self, name: str) -> str:
        """将驼峰命名转换为蛇形命名"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def get_generated_files(self) -> List[str]:
        """获取所有生成的文件路径"""
        return self._generated_files
