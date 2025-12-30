from lxml import etree
from ..models.task import OrmGenerationResult


class OrmXmlParser:
    def parse(self, ai_response: str) -> OrmGenerationResult:
        """解析 AI 返回的 XML"""
        # 清理代码块标记
        cleaned = ai_response.replace("```xml", "").replace("```", "").strip()

        # 使用 lxml 解析
        try:
            root = etree.fromstring(cleaned.encode("utf-8"))

            # 提取实体信息
            entity = root.find(".//entity")
            if entity is None:
                raise ValueError("未找到 entity 标签")

            entity_name = entity.get("name", "app.module.Entity")
            table_name = entity.get("tableName", "entity_table")

            # 获取完整 XML
            xml_content = etree.tostring(root, encoding="unicode")

            return OrmGenerationResult(
                xml=xml_content,
                entity_name=entity_name,
                table_name=table_name,
            )

        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML 解析失败: {e}")
