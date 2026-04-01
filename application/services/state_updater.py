import uuid
from domain.novel.value_objects.chapter_state import ChapterState
from domain.bible.entities.character import Character
from domain.bible.value_objects.character_id import CharacterId
from domain.novel.value_objects.foreshadowing import (
    Foreshadowing,
    ForeshadowingStatus,
    ImportanceLevel
)
from domain.bible.repositories.bible_repository import BibleRepository
from domain.novel.repositories.foreshadowing_repository import ForeshadowingRepository


class StateUpdater:
    """状态更新应用服务

    根据 ChapterState 更新各个领域对象
    """

    def __init__(
        self,
        bible_repository: BibleRepository,
        foreshadowing_repository: ForeshadowingRepository
    ):
        self.bible_repository = bible_repository
        self.foreshadowing_repository = foreshadowing_repository

    def update_from_chapter(
        self,
        novel_id: str,
        chapter_number: int,
        chapter_state: ChapterState
    ) -> None:
        """从章节状态更新所有相关对象

        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            chapter_state: 章节状态

        Raises:
            ValueError: 如果必要的对象不存在
        """
        bible_updated = False
        foreshadowing_updated = False

        # 更新 Bible（新角色）
        if chapter_state.has_new_characters():
            bible = self.bible_repository.get_by_novel_id(novel_id)
            if bible is None:
                raise ValueError(f"Bible not found for novel {novel_id}")

            for char_data in chapter_state.new_characters:
                char_id = CharacterId(str(uuid.uuid4()))
                character = Character(
                    id=char_id,
                    name=char_data["name"],
                    description=char_data["description"]
                )
                bible.add_character(character)

            self.bible_repository.save(bible)
            bible_updated = True

        # 更新 ForeshadowingRegistry（新伏笔和解决伏笔）
        if chapter_state.has_foreshadowing_activity():
            foreshadowing_registry = self.foreshadowing_repository.get_by_novel_id(novel_id)
            if foreshadowing_registry is None:
                raise ValueError(f"ForeshadowingRegistry not found for novel {novel_id}")

            # 添加新伏笔
            for foreshadow_data in chapter_state.foreshadowing_planted:
                foreshadowing = Foreshadowing(
                    id=str(uuid.uuid4()),
                    planted_in_chapter=foreshadow_data["chapter"],
                    description=foreshadow_data["description"],
                    importance=ImportanceLevel.MEDIUM,  # 默认中等重要性
                    status=ForeshadowingStatus.PLANTED
                )
                foreshadowing_registry.register(foreshadowing)

            # 解决伏笔
            for resolved_data in chapter_state.foreshadowing_resolved:
                foreshadowing_registry.mark_resolved(
                    foreshadowing_id=resolved_data["foreshadowing_id"],
                    resolved_in_chapter=resolved_data["chapter"]
                )

            self.foreshadowing_repository.save(foreshadowing_registry)
            foreshadowing_updated = True
