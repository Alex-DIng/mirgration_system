"""
Spring 框架知识 - Spring Framework Knowledge

定义 Spring 框架的核心概念和最佳实践。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AnnotationInfo:
    """注解信息"""
    name: str
    description: str
    usage: str
    example: str


class SpringKnowledge:
    """
    Spring 框架知识库

    提供 Spring 开发相关的知识，用于指导代码生成。
    """

    # 核心注解
    CORE_ANNOTATIONS = {
        "Component": AnnotationInfo(
            name="@Component",
            description="通用组件注解",
            usage="标记一个类为 Spring Bean",
            example="@Component\npublic class MyService {}"
        ),
        "Service": AnnotationInfo(
            name="@Service",
            description="服务层注解",
            usage="标记业务服务类",
            example="@Service\npublic class OrderService {}"
        ),
        "Repository": AnnotationInfo(
            name="@Repository",
            description="数据访问层注解",
            usage="标记 DAO 或 Repository 类",
            example="@Repository\npublic class OrderRepository {}"
        ),
        "Controller": AnnotationInfo(
            name="@Controller",
            description="控制器注解",
            usage="标记 MVC 控制器",
            example="@Controller\npublic class OrderController {}"
        ),
        "RestController": AnnotationInfo(
            name="@RestController",
            description="REST 控制器注解",
            usage="标记 REST API 控制器",
            example="@RestController\n@RequestMapping(\"/api/orders\")\npublic class OrderController {}"
        ),
    }

    # JPA 注解
    JPA_ANNOTATIONS = {
        "Entity": AnnotationInfo(
            name="@Entity",
            description="JPA 实体注解",
            usage="标记一个类为 JPA 实体",
            example="@Entity\n@Table(name = \"orders\")\npublic class Order {}"
        ),
        "Table": AnnotationInfo(
            name="@Table",
            description="表名注解",
            usage="指定数据库表名",
            example="@Table(name = \"securities_order\")"
        ),
        "Id": AnnotationInfo(
            name="@Id",
            description="主键注解",
            usage="标记主键字段",
            example="@Id\n@GeneratedValue(strategy = GenerationType.IDENTITY)\nprivate Long id;"
        ),
        "Column": AnnotationInfo(
            name="@Column",
            description="列注解",
            usage="指定列名和属性",
            example='@Column(name = "order_id", nullable = false)'
        ),
        "GeneratedValue": AnnotationInfo(
            name="@GeneratedValue",
            description="主键生成策略",
            usage="指定主键生成方式",
            example="@GeneratedValue(strategy = GenerationType.IDENTITY)"
        ),
        "OneToMany": AnnotationInfo(
            name="@OneToMany",
            description="一对多关系",
            usage="标记一对多关联",
            example="@OneToMany(mappedBy = \"order\")\nprivate List<OrderItem> items;"
        ),
        "ManyToOne": AnnotationInfo(
            name="@ManyToOne",
            description="多对一关系",
            usage="标记多对一关联",
            example="@ManyToOne\n@JoinColumn(name = \"user_id\")\nprivate User user;"
        ),
    }

    # 事务注解
    TRANSACTION_ANNOTATIONS = {
        "Transactional": AnnotationInfo(
            name="@Transactional",
            description="事务管理注解",
            usage="标记事务边界",
            example="@Transactional\npublic void transfer(...) {}"
        ),
    }

    # Spring Boot 配置类模板
    CONFIG_TEMPLATE = """
package {package}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;

/**
 * 自动配置类
 * 由迁移工具生成
 */
@Configuration
public class {config_name} {

    @Bean
    @ConditionalOnMissingBean
    public {bean_type} {bean_name}() {
        return new {bean_type}();
    }
}
""".strip()

    # REST Controller 模板
    CONTROLLER_TEMPLATE = """
package {package}.controller;

import {package}.entity.{entity};
import {package}.service.{service};
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * {entity} REST 控制器
 */
@RestController
@RequestMapping("{route}")
public class {controller} {

    @Autowired
    private {service} service;

    @GetMapping
    public List<{entity}> getAll() {
        return service.findAll();
    }

    @GetMapping("/{id}")
    public {entity} getById(@PathVariable Long id) {
        return service.findById(id).orElse(null);
    }

    @PostMapping
    public {entity} create(@RequestBody {entity} entity) {
        return service.save(entity);
    }

    @PutMapping("/{id}")
    public {entity} update(@PathVariable Long id, @RequestBody {entity} entity) {
        return service.update(id, entity);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        service.deleteById(id);
    }
}
""".strip()

    @classmethod
    def get_annotation_usage(cls, annotation_name: str) -> Optional[str]:
        """获取注解使用说明"""
        info = cls.CORE_ANNOTATIONS.get(annotation_name)
        if info:
            return f"{info.description}\n\n用法：{info.usage}\n\n示例:\n{info.example}"

        info = cls.JPA_ANNOTATIONS.get(annotation_name)
        if info:
            return f"{info.description}\n\n用法：{info.usage}\n\n示例:\n{info.example}"

        return None

    @classmethod
    def get_jpa_context(cls) -> str:
        """获取 JPA 上下文说明"""
        return """
JPA 实体映射规则:

1. 类级别:
   - @Entity: 标记为 JPA 实体
   - @Table(name = "table_name"): 指定表名

2. 字段级别:
   - @Id: 主键字段
   - @GeneratedValue: 主键生成策略
   - @Column: 列映射

3. 关系映射:
   - @OneToMany: 一对多
   - @ManyToOne: 多对一
   - @ManyToMany: 多对多
   - @OneToOne: 一对一

4. 最佳实践:
   - 使用包装类型 (Integer, Long) 而非基本类型
   - 使用 Lombok @Data 简化代码
   - 实现 equals/hashCode
""".strip()

    @classmethod
    def get_service_context(cls) -> str:
        """获取 Service 层上下文说明"""
        return """
Service 层设计规范:

1. 注解:
   - @Service: 标记服务类
   - @Transactional: 事务管理

2. 依赖注入:
   - 使用 @Autowired 注入 Repository

3. 方法设计:
   - findAll(): 查询所有
   - findById(id): 根据 ID 查询
   - save(entity): 保存
   - update(id, entity): 更新
   - deleteById(id): 删除

4. 事务边界:
   - 写操作需要 @Transactional
   - 读操作可选择性使用 @Transactional(readOnly = true)
""".strip()

    @classmethod
    def validate_spring_code(cls, java_code: str) -> List[str]:
        """
        验证 Java 代码是否符合 Spring 规范

        Args:
            java_code: Java 代码

        Returns:
            警告列表
        """
        warnings = []

        # 检查 Entity 类是否有 @Entity 注解
        if "class " in java_code and "@Entity" not in java_code:
            if "Entity" in java_code or "DTO" in java_code:
                warnings.append("Entity 类应添加 @Entity 注解")

        # 检查 Service 类是否有 @Service 注解
        if "Service" in java_code and "@Service" not in java_code:
            warnings.append("Service 类应添加 @Service 注解")

        # 检查是否有 @Transactional
        if "save(" in java_code or "update(" in java_code:
            if "@Transactional" not in java_code:
                warnings.append("写操作方法应添加 @Transactional 注解")

        return warnings
