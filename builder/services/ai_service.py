from zhipuai import ZhipuAI
from ..config import settings
from pathlib import Path


class AIService:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)

    def generate_orm(self, config_content: str) -> str:
        """调用智谱 AI 生成 ORM"""
        prompt = self._build_prompt(config_content)

        response = self.client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    def _build_prompt(self, config_content: str) -> str:
        """构建完整提示词"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "orm.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        return f"{template}\n\n输入配置:\n{config_content}"
