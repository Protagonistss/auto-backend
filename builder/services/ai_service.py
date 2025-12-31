from zhipuai import ZhipuAI
from ..config import settings
from pathlib import Path
from typing import List, Dict


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

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, use_system_prompt: bool = False) -> str:
        """通用对话接口"""
        full_messages = []

        # 添加系统提示词
        if use_system_prompt:
            system_prompt = self._load_system_prompt()
            full_messages.append({"role": "system", "content": system_prompt})

        # 添加对话历史
        full_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=settings.ai_model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    def _load_system_prompt(self) -> str:
        """加载系统提示词模板（orm.md）"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "orm.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _build_prompt(self, config_content: str) -> str:
        """构建完整提示词"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "orm.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()

        return f"{template}\n\n输入配置:\n{config_content}"
