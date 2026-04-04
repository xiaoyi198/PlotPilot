"""自动 Bible 生成器 - 从小说标题生成完整的人物、地点、风格设定和世界观"""
import logging
import json
from typing import Dict, Any
from domain.ai.services.llm_service import LLMService, GenerationConfig
from domain.ai.value_objects.prompt import Prompt
from application.services.bible_service import BibleService
from application.services.worldbuilding_service import WorldbuildingService

logger = logging.getLogger(__name__)


class AutoBibleGenerator:
    """自动 Bible 生成器

    根据小说标题，使用 LLM 生成：
    - 3-5 个主要人物（主角、配角、对手、导师等）
    - 2-3 个重要地点
    - 文风公约
    - 世界观（5维度框架）
    """

    def __init__(self, llm_service: LLMService, bible_service: BibleService, worldbuilding_service: WorldbuildingService = None):
        self.llm_service = llm_service
        self.bible_service = bible_service
        self.worldbuilding_service = worldbuilding_service

    async def generate_and_save(
        self,
        novel_id: str,
        premise: str,
        target_chapters: int,
        stage: str = "all"
    ) -> Dict[str, Any]:
        """生成并保存 Bible（支持分阶段）

        Args:
            novel_id: 小说 ID
            premise: 故事梗概/创意
            target_chapters: 目标章节数
            stage: 生成阶段 (all/worldbuilding/characters/locations)

        Returns:
            生成的 Bible 数据
        """
        logger.info(f"Generating Bible for novel: {premise[:50]}... (stage: {stage})")

        # 1. 创建空 Bible（如果不存在）
        bible_id = f"{novel_id}-bible"
        try:
            existing_bible = self.bible_service.get_bible_by_novel(novel_id)
            if existing_bible:
                logger.info(f"Bible already exists for novel {novel_id}")
            else:
                logger.info(f"Bible not found for novel {novel_id}, creating new one")
                self.bible_service.create_bible(bible_id, novel_id)
                logger.info(f"Successfully created Bible {bible_id} for novel {novel_id}")
        except Exception as e:
            logger.error(f"Error checking/creating Bible: {e}")
            # 尝试创建
            try:
                self.bible_service.create_bible(bible_id, novel_id)
                logger.info(f"Successfully created Bible {bible_id} for novel {novel_id}")
            except Exception as create_error:
                logger.error(f"Failed to create Bible: {create_error}")
                raise

        # 2. 根据阶段生成不同内容
        if stage == "all":
            # 一次性生成所有内容（向后兼容）
            bible_data = await self._generate_bible_data(premise, target_chapters)
            await self._save_to_bible(novel_id, bible_data)
            if self.worldbuilding_service and "worldbuilding" in bible_data:
                await self._save_worldbuilding(novel_id, bible_data["worldbuilding"])

        elif stage == "worldbuilding":
            # 确保Bible记录存在
            try:
                self.bible_repository.get_bible_by_novel(novel_id)
            except EntityNotFoundError:
                bible_id = f"bible-{novel_id}"
                self.bible_repository.create_bible(bible_id, novel_id)
                logger.info(f"Created Bible record: {bible_id}")

            # 只生成世界观和文风
            bible_data = await self._generate_worldbuilding_and_style(premise, target_chapters)
            # 保存文风
            if "style" in bible_data:
                style_id = f"{novel_id}-style-1"
                try:
                    self.bible_service.add_style_note(
                        novel_id=novel_id,
                        note_id=style_id,
                        category="文风公约",
                        content=bible_data["style"]
                    )
                    logger.info(f"Style note saved: {style_id}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"Style note {style_id} already exists, skipping")
                    else:
                        logger.error(f"Failed to save style note: {e}")
                        raise
            # 保存世界观
            if self.worldbuilding_service and "worldbuilding" in bible_data:
                await self._save_worldbuilding(novel_id, bible_data["worldbuilding"])

        elif stage == "characters":
            # 确保Bible记录存在
            try:
                self.bible_repository.get_bible_by_novel(novel_id)
            except EntityNotFoundError:
                bible_id = f"bible-{novel_id}"
                self.bible_repository.create_bible(bible_id, novel_id)
                logger.info(f"Created Bible record: {bible_id}")

            # 基于已有世界观生成人物
            existing_worldbuilding = self._load_worldbuilding(novel_id)
            bible_data = await self._generate_characters(premise, target_chapters, existing_worldbuilding)
            # 保存人物
            for idx, char_data in enumerate(bible_data.get("characters", [])):
                character_id = f"{novel_id}-char-{idx+1}"
                try:
                    self.bible_service.add_character(
                        novel_id=novel_id,
                        character_id=character_id,
                        name=char_data["name"],
                        description=f"{char_data['role']} - {char_data['description']}"
                    )
                    logger.info(f"Character saved: {character_id}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"Character {character_id} already exists, skipping")
                    else:
                        logger.error(f"Failed to save character: {e}")
                        raise

        elif stage == "locations":
            # 确保Bible记录存在
            try:
                self.bible_repository.get_bible_by_novel(novel_id)
            except EntityNotFoundError:
                bible_id = f"bible-{novel_id}"
                self.bible_repository.create_bible(bible_id, novel_id)
                logger.info(f"Created Bible record: {bible_id}")

            # 基于已有世界观和人物生成地点
            existing_worldbuilding = self._load_worldbuilding(novel_id)
            existing_characters = self._load_characters(novel_id)
            bible_data = await self._generate_locations(premise, target_chapters, existing_worldbuilding, existing_characters)
            # 保存地点
            for idx, loc_data in enumerate(bible_data.get("locations", [])):
                location_id = f"{novel_id}-loc-{idx+1}"
                try:
                    self.bible_service.add_location(
                        novel_id=novel_id,
                        location_id=location_id,
                        name=loc_data["name"],
                        description=loc_data["description"],
                        location_type=loc_data.get("type", "场景")
                    )
                    logger.info(f"Location saved: {location_id}")
                except Exception as e:
                    if "already exists" in str(e):
                        logger.info(f"Location {location_id} already exists, skipping")
                    else:
                        logger.error(f"Failed to save location: {e}")
                        raise

        else:
            raise ValueError(f"Unknown stage: {stage}")

        logger.info(f"Bible generation completed for {novel_id} (stage: {stage})")
        return bible_data

    async def _generate_bible_data(self, premise: str, target_chapters: int) -> Dict[str, Any]:
        """使用 LLM 生成 Bible 数据和世界观"""

        system_prompt = """你是资深网文策划编辑。根据用户提供的故事创意/梗概，生成完整的人物、世界设定和世界观。

**重要：只输出有效的 JSON，不要有任何其他文字。description 字段必须是单行文本，不能有换行符。**

要求：
1. 深入理解故事梗概，提取核心冲突、主题、世界观
2. 至少 3-5 个主要人物（主角、配角、对手、导师等），确保人物之间有冲突和互动
3. 每个人物：姓名、定位（主角/配角/对手/导师）、性格特点、目标动机
4. 至少 2-3 个重要地点，符合故事背景
5. 明确的文风公约（叙事视角、人称、基调、节奏）
6. 完整的世界观（5维度框架）：核心法则、地理生态、社会结构、历史文化、沉浸感细节
7. 人物和地点要符合故事类型（现代都市/古代/玄幻/科幻等）
8. **所有 description 字段必须是单行文本，用逗号或分号分隔不同要点，不要使用换行符**

JSON 格式（不要有其他文字）：
{
  "characters": [
    {
      "name": "人物名",
      "role": "主角/配角/对手/导师",
      "description": "性格、背景、目标、特点，所有内容在一行内，用逗号分隔"
    }
  ],
  "locations": [
    {
      "name": "地点名",
      "type": "城市/建筑/区域",
      "description": "地点描述，单行文本"
    }
  ],
  "style": "第三人称有限视角，以XX视角为主。基调XX，节奏XX。避免XX。营造XX氛围。",
  "worldbuilding": {
    "core_rules": {
      "power_system": "力量体系/科技树的描述",
      "physics_rules": "物理规律的特殊之处",
      "magic_tech": "魔法或科技的运作机制"
    },
    "geography": {
      "terrain": "地形特征",
      "climate": "气候特点",
      "resources": "资源分布",
      "ecology": "生态系统"
    },
    "society": {
      "politics": "政治体制",
      "economy": "经济模式",
      "class_system": "阶级系统"
    },
    "culture": {
      "history": "关键历史事件",
      "religion": "宗教信仰",
      "taboos": "文化禁忌"
    },
    "daily_life": {
      "food_clothing": "衣食住行",
      "language_slang": "俚语与口音",
      "entertainment": "娱乐方式"
    }
  }
}"""

        user_prompt = f"""故事创意：{premise}

目标章节数：{target_chapters}章

请根据这个故事创意，生成完整的人物、世界设定和世界观。注意：
1. 从故事创意中提取关键信息（主角身份、核心能力、故事背景、主要冲突）
2. 人物要有层次，不能只有主角，要有配角、对手、导师等
3. 要有明确的冲突和对立面
4. 世界观要清晰，地点要符合故事类型
5. 文风公约要具体，明确叙事视角、基调、节奏
6. 世界观5个维度都要填写，符合故事类型和背景
7. 适合网文读者，有代入感

只输出 JSON，不要有任何解释文字。"""

        prompt = Prompt(system=system_prompt, user=user_prompt)
        config = GenerationConfig(max_tokens=2048, temperature=0.7)

        result = await self.llm_service.generate(prompt, config)

        # 解析 JSON
        try:
            content = result.content.strip()

            # 移除可能的 markdown 代码块标记
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            content = content.strip()

            # 尝试找到第一个 { 和最后一个 }
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]

            logger.info(f"Attempting to parse Bible JSON (length: {len(content)})")

            # 尝试直接解析
            try:
                bible_data = json.loads(content)
                logger.info(f"Successfully parsed Bible JSON")
                return bible_data
            except json.JSONDecodeError as e:
                # 如果失败，尝试修复常见问题
                logger.warning(f"First parse attempt failed: {e}, trying to repair JSON...")

                # 使用 json.loads 的 strict=False 模式
                import re
                # 移除字符串中的控制字符和多余的空白
                content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)

                bible_data = json.loads(content, strict=False)
                logger.info(f"Successfully parsed Bible JSON after repair")
                return bible_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bible JSON: {e}")
            logger.error(f"Raw content (first 1000 chars): {content[:1000]}")
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

        # 先确保 Bible 记录存在
        try:
            from domain.novel.value_objects.novel_id import NovelId
            existing_bible = self.bible_service.bible_repository.get_by_novel_id(NovelId(novel_id))
            if existing_bible is None:
                # 创建 Bible 记录
                bible_id = f"bible-{novel_id}"
                self.bible_service.create_bible(bible_id=bible_id, novel_id=novel_id)
                logger.info(f"Created Bible record for novel {novel_id}")
        except Exception as e:
            logger.error(f"Failed to ensure Bible exists: {e}")
            return

        # 添加人物
        for idx, char_data in enumerate(bible_data.get("characters", [])):
            character_id = f"{novel_id}-char-{idx+1}"
            try:
                self.bible_service.add_character(
                    novel_id=novel_id,
                    character_id=character_id,
                    name=char_data["name"],
                    description=f"{char_data['role']} - {char_data['description']}"
                )
                logger.info(f"Character saved: {character_id}")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"Character {character_id} already exists, skipping")
                else:
                    logger.error(f"Failed to save character: {e}")
                    raise

        # 添加地点
        for idx, loc_data in enumerate(bible_data.get("locations", [])):
            location_id = f"{novel_id}-loc-{idx+1}"
            try:
                self.bible_service.add_location(
                    novel_id=novel_id,
                    location_id=location_id,
                    name=loc_data["name"],
                    description=loc_data["description"],
                    location_type=loc_data.get("type", "场景")
                )
                logger.info(f"Location saved: {location_id}")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"Location {location_id} already exists, skipping")
                else:
                    logger.error(f"Failed to save location: {e}")
                    raise

        # 添加风格笔记
        style = bible_data.get("style", "")
        if style:
            style_id = f"{novel_id}-style-1"
            try:
                self.bible_service.add_style_note(
                    novel_id=novel_id,
                    note_id=style_id,
                    category="文风公约",
                    content=style
                )
                logger.info(f"Style note saved: {style_id}")
            except Exception as e:
                # 如果已存在则更新
                if "already exists" in str(e):
                    logger.info(f"Style note {style_id} already exists, skipping")
                else:
                    logger.error(f"Failed to save style note: {e}")
                    raise

    async def _save_worldbuilding(self, novel_id: str, worldbuilding_data: Dict[str, Any]) -> None:
        """保存世界观到数据库"""
        if not self.worldbuilding_service:
            logger.warning("WorldbuildingService not available, skipping worldbuilding save")
            return

        try:
            # 创建或更新世界观
            self.worldbuilding_service.update_worldbuilding(
                novel_id=novel_id,
                core_rules=worldbuilding_data.get("core_rules"),
                geography=worldbuilding_data.get("geography"),
                society=worldbuilding_data.get("society"),
                culture=worldbuilding_data.get("culture"),
                daily_life=worldbuilding_data.get("daily_life")
            )
            logger.info(f"Worldbuilding saved for {novel_id}")
        except Exception as e:
            logger.error(f"Failed to save worldbuilding: {e}")

    def _load_worldbuilding(self, novel_id: str) -> Dict[str, Any]:
        """加载已有世界观"""
        if not self.worldbuilding_service:
            return {}
        try:
            wb = self.worldbuilding_service.get_worldbuilding(novel_id)
            return {
                "core_rules": wb.core_rules,
                "geography": wb.geography,
                "society": wb.society,
                "culture": wb.culture,
                "daily_life": wb.daily_life
            }
        except:
            return {}

    def _load_characters(self, novel_id: str) -> list:
        """加载已有人物"""
        try:
            bible = self.bible_service.get_bible(novel_id)
            return [{"name": c.name, "description": c.description} for c in bible.characters]
        except:
            return []

    async def _generate_worldbuilding_and_style(self, premise: str, target_chapters: int) -> Dict[str, Any]:
        """只生成世界观和文风"""
        system_prompt = """你是资深网文策划编辑。根据故事创意生成世界观和文风公约。

**重要：只输出有效的 JSON，不要有任何其他文字。**

要求：
1. 完整的世界观（5维度框架）：核心法则、地理生态、社会结构、历史文化、沉浸感细节
2. 明确的文风公约（叙事视角、人称、基调、节奏）
3. 符合故事类型（现代都市/古代/玄幻/科幻等）

JSON 格式：
{
  "style": "第三人称有限视角，以XX视角为主。基调XX，节奏XX。避免XX。营造XX氛围。",
  "worldbuilding": {
    "core_rules": {
      "power_system": "力量体系/科技树的描述",
      "physics_rules": "物理规律的特殊之处",
      "magic_tech": "魔法或科技的运作机制"
    },
    "geography": {
      "terrain": "地形特征",
      "climate": "气候特点",
      "resources": "资源分布",
      "ecology": "生态系统"
    },
    "society": {
      "politics": "政治体制",
      "economy": "经济模式",
      "class_system": "阶级系统"
    },
    "culture": {
      "history": "关键历史事件",
      "religion": "宗教信仰",
      "taboos": "文化禁忌"
    },
    "daily_life": {
      "food_clothing": "衣食住行",
      "language_slang": "俚语与口音",
      "entertainment": "娱乐方式"
    }
  }
}"""

        user_prompt = f"""故事创意：{premise}

目标章节数：{target_chapters}章

请生成世界观和文风公约。只输出 JSON，不要有任何解释文字。"""

        return await self._call_llm_and_parse(system_prompt, user_prompt)

    async def _generate_characters(self, premise: str, target_chapters: int, worldbuilding: Dict[str, Any]) -> Dict[str, Any]:
        """基于世界观生成人物"""
        wb_summary = self._summarize_worldbuilding(worldbuilding)

        system_prompt = """你是资深网文策划编辑。基于已有世界观生成主要人物。

**重要：只输出有效的 JSON，不要有任何其他文字。description 字段必须是单行文本。**

要求：
1. 至少 3-5 个主要人物（主角、配角、对手、导师等）
2. 人物要符合世界观设定
3. 确保人物之间有冲突和互动
4. 每个人物：姓名、定位、性格特点、目标动机

JSON 格式：
{
  "characters": [
    {
      "name": "人物名",
      "role": "主角/配角/对手/导师",
      "description": "性格、背景、目标、特点，所有内容在一行内，用逗号分隔"
    }
  ]
}"""

        user_prompt = f"""故事创意：{premise}

已有世界观：
{wb_summary}

请基于这个世界观生成主要人物。只输出 JSON，不要有任何解释文字。"""

        return await self._call_llm_and_parse(system_prompt, user_prompt)

    async def _generate_locations(self, premise: str, target_chapters: int, worldbuilding: Dict[str, Any], characters: list) -> Dict[str, Any]:
        """基于世界观和人物生成地点"""
        wb_summary = self._summarize_worldbuilding(worldbuilding)
        char_summary = "\n".join([f"- {c['name']}: {c['description'][:50]}..." for c in characters])

        system_prompt = """你是资深网文策划编辑。基于已有世界观和人物生成完整地图。

**重要：只输出有效的 JSON，不要有任何其他文字。**

要求：
1. 至少 5-10 个重要地点，构成完整地图
2. 地点要符合世界观设定
3. 考虑人物的活动范围和故事需要
4. 包含不同类型：城市、建筑、区域、特殊场所等

JSON 格式：
{
  "locations": [
    {
      "name": "地点名",
      "type": "城市/建筑/区域/特殊场所",
      "description": "地点描述，单行文本"
    }
  ]
}"""

        user_prompt = f"""故事创意：{premise}

已有世界观：
{wb_summary}

已有人物：
{char_summary}

请基于世界观和人物生成完整地图。只输出 JSON，不要有任何解释文字。"""

        return await self._call_llm_and_parse(system_prompt, user_prompt)

    def _summarize_worldbuilding(self, wb: Dict[str, Any]) -> str:
        """总结世界观为文本"""
        if not wb:
            return "无"

        parts = []
        for key, value in wb.items():
            if isinstance(value, dict):
                items = ", ".join([f"{k}: {v}" for k, v in value.items() if v])
                parts.append(f"{key}: {items}")
        return "\n".join(parts)

    async def _call_llm_and_parse(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """调用 LLM 并解析 JSON"""
        prompt = Prompt(system=system_prompt, user=user_prompt)
        config = GenerationConfig(max_tokens=2048, temperature=0.7)
        result = await self.llm_service.generate(prompt, config)

        try:
            content = result.content.strip()

            # 移除可能的 markdown 代码块标记
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            content = content.strip()

            # 尝试找到第一个 { 和最后一个 }
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]

            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw content: {content[:500]}")
            return {}

