"""自动 Bible 生成器 - 从小说标题生成完整的人物、地点、风格设定"""
import logging
import json
from typing import Dict, Any
from domain.ai.services.llm_service import LLMService, GenerationConfig
from domain.ai.value_objects.prompt import Prompt
from application.services.bible_service import BibleService

logger = logging.getLogger(__name__)


class AutoBibleGenerator:
    """自动 Bible 生成器

    根据小说标题，使用 LLM 生成：
    - 3-5 个主要人物（主角、配角、对手、导师等）
    - 2-3 个重要地点
    - 文风公约
    """

    def __init__(self, llm_service: LLMService, bible_service: BibleService):
        self.llm_service = llm_service
        self.bible_service = bible_service

    async def generate_and_save(
        self,
        novel_id: str,
        title: str,
        target_chapters: int
    ) -> Dict[str, Any]:
        """生成并保存 Bible

        Args:
            novel_id: 小说 ID
            title: 小说标题
            target_chapters: 目标章节数

        Returns:
            生成的 Bible 数据
        """
        logger.info(f"Generating Bible for novel: {title}")

        # 1. 创建空 Bible
        bible_id = f"{novel_id}-bible"
        self.bible_service.create_bible(bible_id, novel_id)

        # 2. 用 LLM 生成设定
        bible_data = await self._generate_bible_data(title, target_chapters)

        # 3. 保存到 Bible
        await self._save_to_bible(novel_id, bible_data)

        logger.info(f"Bible generated successfully for {novel_id}")
        return bible_data

    async def _generate_bible_data(self, title: str, target_chapters: int) -> Dict[str, Any]:
        """使用 LLM 生成 Bible 数据"""

        system_prompt = """你是资深网文策划编辑。根据小说标题，生成完整的人物和世界设定。

要求：
1. 至少 3-5 个主要人物（主角、配角、对手、导师等），确保人物之间有冲突和互动
2. 每个人物：姓名、定位（主角/配角/对手/导师）、性格特点、目标动机
3. 至少 2-3 个重要地点
4. 明确的文风公约（叙事视角、基调）

以 JSON 格式输出：
{
  "characters": [
    {
      "name": "人物名",
      "role": "主角/配角/对手/导师",
      "description": "性格、背景、目标、特点（100-200字）"
    }
  ],
  "locations": [
    {
      "name": "地点名",
      "type": "城市/建筑/区域",
      "description": "地点描述"
    }
  ],
  "style": "第三人称有限视角，轻松幽默基调，避免过度血腥暴力"
}"""

        user_prompt = f"""小说标题：《{title}》
目标章节数：{target_chapters}章

请生成这部小说的完整设定。确保：
1. 人物要有层次，不能只有主角
2. 要有明确的冲突和对立面
3. 世界观要清晰
4. 适合网文读者"""

        prompt = Prompt(system=system_prompt, user=user_prompt)
        config = GenerationConfig(max_tokens=2048, temperature=0.8)

        result = await self.llm_service.generate(prompt, config)

        # 解析 JSON
        try:
            content = result.content.strip()
            # 移除可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            bible_data = json.loads(content)
            return bible_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bible JSON: {e}")
            # 返回默认结构
            return {
                "characters": [
                    {
                        "name": "主角",
                        "role": "主角",
                        "description": "待补充"
                    }
                ],
                "locations": [
                    {
                        "name": "主要场景",
                        "type": "城市",
                        "description": "待补充"
                    }
                ],
                "style": "第三人称有限视角，轻松幽默"
            }

    async def _save_to_bible(self, novel_id: str, bible_data: Dict[str, Any]) -> None:
        """保存到 Bible"""

        # 添加人物
        for idx, char_data in enumerate(bible_data.get("characters", [])):
            character_id = f"{novel_id}-char-{idx+1}"
            self.bible_service.add_character(
                novel_id=novel_id,
                character_id=character_id,
                name=char_data["name"],
                description=f"{char_data['role']} - {char_data['description']}"
            )

        # 添加地点
        for idx, loc_data in enumerate(bible_data.get("locations", [])):
            location_id = f"{novel_id}-loc-{idx+1}"
            self.bible_service.add_location(
                novel_id=novel_id,
                location_id=location_id,
                name=loc_data["name"],
                description=loc_data["description"],
                location_type=loc_data.get("type", "场景")
            )

        # 添加风格笔记
        style = bible_data.get("style", "")
        if style:
            style_id = f"{novel_id}-style-1"
            self.bible_service.add_style_note(
                novel_id=novel_id,
                note_id=style_id,
                category="文风公约",
                content=style
            )
