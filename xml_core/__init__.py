"""XML 核心包 - 通用 XML 处理库

提供 XML 解析、合并、命名空间处理等通用功能。
"""

from pathlib import Path
from typing import Optional

from .merger import XmlMerger, MergeResult
from .parser import XmlParser
from .formatter import XmlFormatter
from .namespace import NamespaceHandler
from .config.settings import XmlCoreSettings, MergeOptions
from .exceptions import (
    XmlCoreError,
    XmlParseError,
    XmlMergeError,
    XmlFileNotFoundError,
    XmlValidationError
)


__version__ = "0.1.0"
__all__ = [
    "XmlCore",
    "XmlMerger",
    "XmlParser",
    "XmlFormatter",
    "NamespaceHandler",
    "MergeResult",
    "XmlCoreSettings",
    "MergeOptions",
    "XmlCoreError",
    "XmlParseError",
    "XmlMergeError",
    "XmlFileNotFoundError",
    "XmlValidationError",
]


class XmlCore:
    """
    XML 核心类 - 统一的 XML 处理入口

    示例用法:
        # 基础用法
        core = XmlCore("config.xml")
        result = core.merge_element(
            element_xml='<setting key="timeout" value="30"/>',
            parent_xpath=".//settings",
            element_matcher="key"
        )

        # ORM 场景
        core = XmlCore.for_orm("app.orm.xml")
        result = core.merge_entity(entity_xml)
    """

    def __init__(
        self,
        xml_path: str,
        encoding: str = "utf-8",
        pretty_print: bool = True,
        xml_declaration: bool = True
    ):
        """
        初始化 XmlCore

        Args:
            xml_path: XML 文件路径
            encoding: 文件编码
            pretty_print: 是否美化输出
            xml_declaration: 是否包含 XML 声明
        """
        self.settings = XmlCoreSettings(
            xml_path=Path(xml_path),
            encoding=encoding,
            pretty_print=pretty_print,
            xml_declaration=xml_declaration
        )

        self.merger = XmlMerger(
            xml_path=str(self.settings.xml_path),
            encoding=encoding
        )
        self.parser = XmlParser(encoding=encoding)
        self.formatter = XmlFormatter(
            encoding=encoding,
            pretty_print=pretty_print,
            xml_declaration=xml_declaration
        )
        self.ns_handler = NamespaceHandler()

    def merge_element(
        self,
        element_xml: str,
        parent_xpath: str,
        element_matcher: Optional[str] = None,
        merge_strategy: str = "replace_or_append",
        strip_ns_on_children: bool = True
    ) -> MergeResult:
        """
        合并 XML 元素到文件

        Args:
            element_xml: 元素 XML 片段
            parent_xpath: 父容器 XPath
            element_matcher: 元素匹配属性名（如 'name', 'id', 'key'）
            merge_strategy: 合并策略
            strip_ns_on_children: 是否移除子元素的命名空间声明

        Returns:
            MergeResult: 合并结果
        """
        options = MergeOptions(
            parent_xpath=parent_xpath,
            element_matcher=element_matcher,
            merge_strategy=merge_strategy,
            strip_ns_on_children=strip_ns_on_children
        )
        return self.merger.merge_element(element_xml, options)

    def merge_entity(
        self,
        entity_xml: str,
        entities_xpath: str = ".//entities"
    ) -> MergeResult:
        """
        合并 ORM 实体（便捷方法）

        Args:
            entity_xml: 实体 XML 片段
            entities_xpath: entities 容器 XPath

        Returns:
            MergeResult: 合并结果
        """
        return self.merge_element(
            element_xml=entity_xml,
            parent_xpath=entities_xpath,
            element_matcher="name"
        )

    @classmethod
    def for_orm(
        cls,
        xml_path: str,
        encoding: str = "utf-8"
    ) -> "XmlCore":
        """
        创建用于 ORM XML 的 XmlCore 实例（工厂方法）

        Args:
            xml_path: ORM XML 文件路径
            encoding: 文件编码

        Returns:
            XmlCore 实例
        """
        return cls(xml_path=xml_path, encoding=encoding)

    def find_element(
        self,
        xpath: str,
        namespace_map: Optional[dict] = None
    ):
        """
        查找元素

        Args:
            xpath: XPath 表达式
            namespace_map: 命名空间映射

        Returns:
            找到的元素，未找到返回 None
        """
        return self.merger.find_element(xpath, namespace_map)

    def parse_file(self):
        """
        解析 XML 文件

        Returns:
            ElementTree 对象
        """
        return self.parser.parse_file(str(self.settings.xml_path))

    def format_element(self, element) -> str:
        """
        格式化元素

        Args:
            element: Element 对象

        Returns:
            格式化后的 XML 字符串
        """
        return self.formatter.format_element(element)
