from lxml import etree
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import re

from ..config import settings


class WriteEntityResult(BaseModel):
    """写入结果"""
    entity_name: str
    action: str  # created/updated


class OrmXmlService:
    """ORM XML 文件操作服务"""

    def __init__(self):
        self.xml_file_path = Path(settings.orm_xml_path)
        self._namespace_map = {
            'x': '/nop/schema/xdsl.xdef',
            'xpl': '/nop/schema/xpl.xdef'
        }

    def write_entity(self, entity_xml: str) -> WriteEntityResult:
        """
        智能合并 entity 到 app.orm.xml

        Args:
            entity_xml: entity XML 片段

        Returns:
            WriteEntityResult: 写入结果

        Raises:
            ValueError: XML 解析失败或缺少必填字段
            FileNotFoundError: 文件不存在
            IOError: 文件操作失败
        """
        # 1. 解析输入的 entity XML
        new_entity = self._parse_entity_xml(entity_xml)
        entity_name = new_entity.get("name")

        if not entity_name:
            raise ValueError("entity 标签缺少必填的 name 属性")

        # 2. 读取目标文件
        if not self.xml_file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.xml_file_path}")

        parser = etree.XMLParser(remove_blank_text=False, remove_comments=False)
        tree = etree.parse(self.xml_file_path, parser)
        root = tree.getroot()

        # 3. 查找 entities 节点
        entities_node = root.find(".//entities", self._namespace_map)
        if entities_node is None:
            raise ValueError("app.orm.xml 中未找到 entities 节点")

        # 4. 检查是否重复
        existing_entity = self._find_entity_by_name(root, entity_name)

        if existing_entity is not None:
            # 替换
            entities_node.replace(existing_entity, new_entity)
            action = "updated"
        else:
            # 追加
            entities_node.append(new_entity)
            action = "created"

        # 5. 写回文件
        self._write_tree(tree)

        return WriteEntityResult(
            entity_name=entity_name,
            action=action
        )

    def _parse_entity_xml(self, xml: str) -> etree._Element:
        """
        解析 entity XML 片段

        Args:
            xml: entity XML 字符串

        Returns:
            lxml Element 对象

        Raises:
            ValueError: XML 解析失败或未找到 entity 标签
        """
        # 清理代码块标记
        cleaned = xml.replace("```xml", "").replace("```", "").strip()

        # 在 entity 开始标签中添加所有必要的命名空间声明
        # 匹配 <entity 后跟任意字符（包括换行）
        cleaned = re.sub(
            r'<entity(\s+)',
            r'<entity xmlns:biz="biz" xmlns:ext="ext" xmlns:orm="orm" xmlns:i18n-en="i18n-en" xmlns:ui="ui"\1',
            cleaned,
            count=1
        )

        # 调试：打印处理后的 XML（前200字符）
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"处理后的 XML: {cleaned[:200]}...")

        parser = etree.XMLParser(remove_blank_text=False)

        try:
            # 直接解析
            entity = etree.fromstring(cleaned.encode("utf-8"), parser)
            if entity.tag != "entity":
                # 如果根元素不是 entity，查找第一个 entity 子元素
                entity = entity.find(".//entity")
            if entity is None:
                raise ValueError("未找到 entity 标签")
            return entity
        except Exception as e:
            logger.error(f"XML 解析失败: {e}\nXML 内容: {cleaned[:500]}")
            raise ValueError(f"XML 解析失败: {e}")

    def _find_entity_by_name(self, root: etree._Element, entity_name: str) -> Optional[etree._Element]:
        """
        查找指定名称的 entity

        Args:
            root: XML 根节点
            entity_name: entity 的 name 属性值

        Returns:
            找到的 entity 节点，未找到返回 None
        """
        entities_node = root.find(".//entities", self._namespace_map)
        if entities_node is None:
            return None

        for entity in entities_node.findall("entity"):
            if entity.get("name") == entity_name:
                return entity
        return None

    def _write_tree(self, tree: etree._ElementTree):
        """
        写回文件，保持格式

        Args:
            tree: lxml ElementTree 对象
        """
        # 使用 indent 方法格式化 XML（lxml 4.9+）
        try:
            etree.indent(tree, space="  ")
        except AttributeError:
            # 如果 lxml 版本过低，跳过 indent
            pass

        xml_content = etree.tostring(
            tree,
            encoding="utf-8",
            pretty_print=True,
            xml_declaration=True
        )

        with open(self.xml_file_path, "wb") as f:
            f.write(xml_content)
