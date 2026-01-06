"""XML 命名空间处理器"""

import re
from typing import List, Set, Optional
from lxml import etree


class NamespaceHandler:
    """XML 命名空间处理"""

    # 常见命名空间前缀
    COMMON_PREFIXES = ['biz', 'ext', 'orm', 'i18n-en', 'ui', 'x', 'xpl', 'xs']

    @staticmethod
    def detect_used_namespaces(xml: str) -> Set[str]:
        """
        检测 XML 中使用的命名空间前缀

        Args:
            xml: XML 字符串

        Returns:
            使用的命名空间前缀集合
        """
        used_namespaces = set()
        for prefix in NamespaceHandler.COMMON_PREFIXES:
            if f'{prefix}:' in xml:
                used_namespaces.add(prefix)
        return used_namespaces

    @staticmethod
    def build_namespace_declarations(prefixes: Set[str]) -> List[str]:
        """
        构建命名空间声明列表

        Args:
            prefixes: 命名空间前缀集合

        Returns:
            命名空间声明字符串列表
        """
        declarations = []
        for prefix in prefixes:
            declarations.append(f'xmlns:{prefix}="{prefix}"')
        return declarations

    @staticmethod
    def ensure_namespaces_in_file(file_path: str, encoding: str = "utf-8") -> None:
        """
        确保文件的根元素包含所有必需的命名空间声明

        Args:
            file_path: XML 文件路径
            encoding: 文件编码
        """
        with open(file_path, 'r', encoding=encoding) as f:
            file_content = f.read()

        # 检测文件中使用的命名空间
        used_namespaces = NamespaceHandler.detect_used_namespaces(file_content)

        if not used_namespaces:
            return

        # 跳过 XML 声明，查找根元素（如 <orm>）
        # 从文件中查找第一个不在声明位置的 <
        # XML 声明格式：<?xml ...?>，所以根元素应该在 ?> 之后
        decl_end = file_content.find('?>')
        if decl_end == -1:
            # 没有 XML 声明，从头开始查找
            search_start = 0
        else:
            # 从 XML 声明结束后开始查找
            search_start = decl_end + 2

        # 找到根元素开始标签
        root_start = file_content.find('<', search_start)
        if root_start == -1:
            return

        root_end = file_content.find('>', root_start)
        if root_end == -1:
            return

        root_tag = file_content[root_start:root_end + 1]

        # 添加缺失的命名空间声明
        modified = False
        new_namespaces = []
        for prefix in used_namespaces:
            ns_decl = f'xmlns:{prefix}="{prefix}"'
            if ns_decl not in root_tag and f'xmlns:{prefix}=' not in root_tag:
                new_namespaces.append(ns_decl)
                modified = True

        if modified:
            # 重新构建根元素标签
            # 提取标签名（例如 "orm"）
            tag_name_start = root_tag.find('<') + 1
            tag_name_end = root_tag.find(' ')
            if tag_name_end == -1:
                tag_name_end = root_tag.find('>')
            tag_name = root_tag[tag_name_start:tag_name_end]

            # 提取现有属性（如果有）
            if '>' in root_tag:
                attrs_part = root_tag[tag_name_end:-1] if tag_name_end != -1 else ''
            else:
                attrs_part = ''

            # 重新构建：<tagName newNamespaces existingAttrs>
            if new_namespaces:
                all_ns = ' '.join(new_namespaces)
                if attrs_part and attrs_part.strip():
                    root_tag = f'<{tag_name} {all_ns} {attrs_part}>'
                else:
                    root_tag = f'<{tag_name} {all_ns}>'

            # 替换文件内容
            file_content = file_content[:root_start] + root_tag + file_content[root_end + 1:]

            # 重新写入修复后的文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(file_content)

    @staticmethod
    def strip_child_namespace_declarations(xml_str: str) -> str:
        """
        移除子元素上的命名空间声明（保留根元素的）

        Args:
            xml_str: XML 字符串

        Returns:
            处理后的 XML 字符串
        """
        def remove_ns_attrs(match):
            tag_name = match.group(1)
            attrs = match.group(2)
            # 移除 xmlns:xxx="xxx" 格式的属性
            cleaned_attrs = re.sub(r'\s+xmlns:[a-z0-9\-]+="[^"]*"', '', attrs)
            return f'<{tag_name}{cleaned_attrs}>'

        # 对常见子元素标签移除 xmlns 声明
        result = re.sub(
            r'<(entity|column|comment|setting|property|item|field|element)([^>]*)>',
            remove_ns_attrs,
            xml_str
        )
        return result

    @staticmethod
    def prepare_namespace_wrapper(xml: str) -> tuple[str, dict]:
        """
        为 XML 片段准备命名空间包装

        Args:
            xml: XML 片段

        Returns:
            (包装后的 XML, 命名空间映射字典)
        """
        cleaned = xml.replace("```xml", "").replace("```", "").strip()

        # 检测实际使用的命名空间
        used_namespaces = NamespaceHandler.detect_used_namespaces(cleaned)

        # 构建命名空间映射
        ns_map = {}
        for prefix in used_namespaces:
            ns_map[prefix] = prefix

        # 如果使用了命名空间前缀，临时包装以提供命名空间上下文
        if used_namespaces:
            ns_decls = ' '.join([f'xmlns:{p}="{p}"' for p in used_namespaces])
            wrapper = f'<root {ns_decls}>{cleaned}</root>'
        else:
            wrapper = f'<root>{cleaned}</root>'

        return wrapper, ns_map

    @staticmethod
    def get_default_namespace_map() -> dict:
        """
        获取默认命名空间映射

        Returns:
            命名空间映射字典
        """
        return {
            'x': '/nop/schema/xdsl.xdef',
            'xpl': '/nop/schema/xpl.xdef'
        }
