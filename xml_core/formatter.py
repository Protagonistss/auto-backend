"""XML 格式化器"""

from pathlib import Path
from typing import Optional
from lxml import etree

from .namespace import NamespaceHandler


class XmlFormatter:
    """XML 格式化器"""

    def __init__(
        self,
        encoding: str = "utf-8",
        pretty_print: bool = True,
        xml_declaration: bool = True
    ):
        """
        初始化格式化器

        Args:
            encoding: 文件编码
            pretty_print: 是否美化输出
            xml_declaration: 是否包含 XML 声明
        """
        self.encoding = encoding
        self.pretty_print = pretty_print
        self.xml_declaration = xml_declaration
        self.ns_handler = NamespaceHandler()

    def serialize(
        self,
        tree: etree._ElementTree,
        strip_child_ns: bool = True
    ) -> str:
        """
        序列化 XML 树为字符串

        Args:
            tree: ElementTree 对象
            strip_child_ns: 是否移除子元素的命名空间声明

        Returns:
            XML 字符串
        """
        xml_content = etree.tostring(
            tree,
            encoding=self.encoding,
            pretty_print=self.pretty_print,
            xml_declaration=self.xml_declaration
        )

        xml_str = xml_content.decode(self.encoding)

        # 移除子元素的命名空间声明
        if strip_child_ns:
            xml_str = self.ns_handler.strip_child_namespace_declarations(xml_str)

        return xml_str

    def write_tree(
        self,
        tree: etree._ElementTree,
        file_path: str,
        strip_child_ns: bool = True,
        auto_add_namespaces: bool = True
    ) -> None:
        """
        写入 XML 树到文件

        Args:
            tree: ElementTree 对象
            file_path: 文件路径
            strip_child_ns: 是否移除子元素的命名空间声明
            auto_add_namespaces: 是否自动添加命名空间声明（默认 True）
        """
        # 序列化树
        xml_str = self.serialize(tree, strip_child_ns=strip_child_ns)

        # 自动添加命名空间（默认启用，确保 XML 格式正确）
        if auto_add_namespaces:
            # 检测使用的命名空间
            used_namespaces = NamespaceHandler.detect_used_namespaces(xml_str)

            # 只添加 NOP 框架预定义的命名空间（i18n-en, ui 等）
            nop_namespaces = {'i18n-en', 'ui', 'ext', 'biz'}
            filtered_namespaces = used_namespaces & nop_namespaces

            if filtered_namespaces:
                # 查找根元素并添加缺失的命名空间声明
                # 跳过 XML 声明
                decl_end = xml_str.find('?>')
                search_start = decl_end + 2 if decl_end != -1 else 0

                # 找到根元素开始标签
                root_start = xml_str.find('<', search_start)
                if root_start != -1:
                    root_end = xml_str.find('>', root_start)
                    if root_end != -1:
                        root_tag = xml_str[root_start:root_end + 1]

                        # 添加缺失的命名空间声明
                        modified = False
                        new_namespaces = []
                        for prefix in sorted(filtered_namespaces):  # 排序确保稳定顺序
                            ns_decl = f'xmlns:{prefix}="{prefix}"'
                            if ns_decl not in root_tag and f'xmlns:{prefix}=' not in root_tag:
                                new_namespaces.append(ns_decl)
                                modified = True

                        if modified:
                            # 重新构建根元素标签
                            tag_name_start = root_tag.find('<') + 1
                            tag_name_end = root_tag.find(' ')
                            if tag_name_end == -1:
                                tag_name_end = root_tag.find('>')
                            tag_name = root_tag[tag_name_start:tag_name_end]

                            # 提取现有属性
                            if tag_name_end != -1:
                                attrs_part = root_tag[tag_name_end:-1]
                            else:
                                attrs_part = ''

                            # 重新构建根元素标签
                            if new_namespaces:
                                all_ns = ' '.join(new_namespaces)
                                if attrs_part and attrs_part.strip():
                                    new_root_tag = f'<{tag_name} {all_ns} {attrs_part}>'
                                else:
                                    new_root_tag = f'<{tag_name} {all_ns}>'

                                # 替换根元素标签
                                xml_str = xml_str[:root_start] + new_root_tag + xml_str[root_end + 1:]

        with open(file_path, "wb") as f:
            f.write(xml_str.encode(self.encoding))

    def format_element(
        self,
        element: etree._Element,
        strip_child_ns: bool = True
    ) -> str:
        """
        格式化单个元素

        Args:
            element: Element 对象
            strip_child_ns: 是否移除子元素的命名空间声明

        Returns:
            XML 字符串
        """
        xml_content = etree.tostring(
            element,
            encoding=self.encoding,
            pretty_print=self.pretty_print
        )

        xml_str = xml_content.decode(self.encoding)

        if strip_child_ns:
            xml_str = self.ns_handler.strip_child_namespace_declarations(xml_str)

        return xml_str

    def prettify(self, xml: str) -> str:
        """
        美化 XML 字符串

        Args:
            xml: XML 字符串

        Returns:
            美化后的 XML 字符串
        """
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml.encode(self.encoding), parser)
            return etree.tostring(
                root,
                encoding=self.encoding,
                pretty_print=True
            ).decode(self.encoding)
        except Exception:
            # 如果解析失败，返回原字符串
            return xml
