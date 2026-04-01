import json
from domain.ai.services.llm_service import LLMService, GenerationConfig
from domain.ai.value_objects.prompt import Prompt
from domain.novel.value_objects.chapter_state import ChapterState


class StateExtractor:
    """状态提取应用服务

    使用 LLM 从章节内容中提取结构化信息
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def extract_chapter_state(self, content: str) -> ChapterState:
        """从章节内容中提取状态

        Args:
            content: 章节内容

        Returns:
            提取的章节状态
        """
        # 构建提取提示词
        system_prompt, user_prompt = self._build_extraction_prompt(content)
        prompt = Prompt(system=system_prompt, user=user_prompt)

        # 配置 LLM
        config = GenerationConfig(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.3  # 较低温度以获得更一致的结构化输出
        )

        # 调用 LLM 生成
        result = await self.llm_service.generate(prompt=prompt, config=config)

        # 解析 JSON 结果
        try:
            data = json.loads(result.content)
        except json.JSONDecodeError:
            # 如果解析失败，返回空状态
            data = {
                "new_characters": [],
                "character_actions": [],
                "relationship_changes": [],
                "foreshadowing_planted": [],
                "foreshadowing_resolved": [],
                "events": []
            }

        # 构建 ChapterState
        return ChapterState(
            new_characters=data.get("new_characters", []),
            character_actions=data.get("character_actions", []),
            relationship_changes=data.get("relationship_changes", []),
            foreshadowing_planted=data.get("foreshadowing_planted", []),
            foreshadowing_resolved=data.get("foreshadowing_resolved", []),
            events=data.get("events", [])
        )

    def _build_extraction_prompt(self, content: str) -> tuple[str, str]:
        """构建提取提示词

        Args:
            content: 章节内容

        Returns:
            (system_prompt, user_prompt) 元组
        """
        system_prompt = """你是一个专业的小说内容分析助手。你的任务是从章节内容中提取结构化信息。

请提取以下信息并以 JSON 格式返回：
1. new_characters: 新出现的角色列表，每个角色包含 name（名字）、description（描述）、first_appearance（首次出现章节号）
2. character_actions: 角色行为列表，每个行为包含 character_id（角色ID）、action（行为描述）、chapter（章节号）
3. relationship_changes: 关系变化列表，每个变化包含 char1（角色1 ID）、char2（角色2 ID）、old_type（旧关系类型）、new_type（新关系类型）、chapter（章节号）
4. foreshadowing_planted: 埋下的伏笔列表，每个伏笔包含 description（描述）、chapter（章节号）
5. foreshadowing_resolved: 解决的伏笔列表，每个解决包含 foreshadowing_id（伏笔ID）、chapter（章节号）
6. events: 事件列表，每个事件包含 type（类型）、description（描述）、involved_characters（涉及的角色ID列表）、chapter（章节号）

返回格式：
{
  "new_characters": [...],
  "character_actions": [...],
  "relationship_changes": [...],
  "foreshadowing_planted": [...],
  "foreshadowing_resolved": [...],
  "events": [...]
}

只返回 JSON，不要包含其他文本。"""

        user_prompt = f"""请从以下章节内容中提取结构化信息：

{content}"""

        return system_prompt, user_prompt
