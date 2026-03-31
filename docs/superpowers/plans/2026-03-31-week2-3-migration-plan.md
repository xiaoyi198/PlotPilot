# Week 2-3 合并计划：功能扩展 + 旧代码迁移

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 扩展 DDD 架构功能，迁移旧代码到新架构，清理无用代码

**Architecture:** 在 Week 1 DDD 基础上扩展，逐步迁移旧 web/ 和 pipeline/ 代码

**Duration:** 2 周合并执行

---

## 阶段划分

### 第一阶段：扩展核心功能（Day 1-7）
- 实现 Chapter 仓储
- 实现 Bible 领域
- 实现 AI 生成服务
- 扩展应用层服务

### 第二阶段：迁移和清理（Day 8-14）
- 迁移 web/app.py 路由到新架构
- 迁移 pipeline/ 到新架构
- 清理旧代码
- 前端适配新 API

---

## 第一阶段任务（Day 1-7）

### Task 11: 实现 Chapter 仓储

**目标：** 创建 ChapterRepository 实现，支持按 Novel 查询章节

**文件：**
- 创建：`infrastructure/persistence/mappers/chapter_mapper.py`
- 创建：`infrastructure/persistence/repositories/file_chapter_repository.py`
- 创建：`tests/integration/infrastructure/persistence/repositories/test_file_chapter_repository.py`

**步骤：**

1. 实现 ChapterMapper
```python
class ChapterMapper:
    @staticmethod
    def to_dict(chapter: Chapter) -> Dict[str, Any]:
        return {
            "id": chapter.chapter_id.value,
            "novel_id": chapter.novel_id.value,
            "number": chapter.number,
            "title": chapter.title,
            "content": chapter.content.value,
            "word_count": chapter.word_count.value
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Chapter:
        # 验证必需字段
        # 创建 Chapter 实体
```

2. 实现 FileChapterRepository
```python
class FileChapterRepository(ChapterRepository):
    def save(self, chapter: Chapter) -> None:
        path = f"novels/{chapter.novel_id.value}/chapters/{chapter.chapter_id.value}.json"
        # 保存章节

    def get_by_id(self, chapter_id: ChapterId) -> Optional[Chapter]:
        # 查询章节

    def list_by_novel(self, novel_id: NovelId) -> List[Chapter]:
        # 按小说 ID 查询所有章节
        # 按 number 排序

    def delete(self, chapter_id: ChapterId) -> None:
        # 删除章节

    def exists(self, chapter_id: ChapterId) -> bool:
        # 检查存在
```

3. 编写集成测试（8 个测试）

4. 提交
```bash
git commit -m "feat(infrastructure): 实现 Chapter 仓储

- 创建 ChapterMapper 数据映射器
- 实现 FileChapterRepository
- 支持按小说查询和排序
- 添加 8 个集成测试"
```

---

### Task 12: 实现 Bible 领域

**目标：** 创建 Bible 聚合根和相关实体

**文件：**
- 创建：`domain/bible/__init__.py`
- 创建：`domain/bible/entities/bible.py`
- 创建：`domain/bible/entities/character.py`
- 创建：`domain/bible/entities/world_setting.py`
- 创建：`domain/bible/value_objects/character_id.py`
- 创建：`domain/bible/repositories/bible_repository.py`
- 创建：`tests/unit/domain/bible/test_bible.py`

**步骤：**

1. 实现 CharacterId 值对象
```python
@dataclass(frozen=True)
class CharacterId:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Character ID cannot be empty")
```

2. 实现 Character 实体
```python
class Character(BaseEntity):
    def __init__(
        self,
        id: CharacterId,
        name: str,
        description: str,
        relationships: List[str] = None
    ):
        super().__init__(id.value)
        self.character_id = id
        self.name = name
        self.description = description
        self.relationships = relationships or []
```

3. 实现 WorldSetting 实体
```python
class WorldSetting(BaseEntity):
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        setting_type: str  # "location", "item", "rule"
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.setting_type = setting_type
```

4. 实现 Bible 聚合根
```python
class Bible(BaseEntity):
    def __init__(self, id: str, novel_id: NovelId):
        super().__init__(id)
        self.novel_id = novel_id
        self.characters: List[Character] = []
        self.world_settings: List[WorldSetting] = []

    def add_character(self, character: Character) -> None:
        # 添加人物

    def add_world_setting(self, setting: WorldSetting) -> None:
        # 添加设定
```

5. 编写单元测试（15 个测试）

6. 提交
```bash
git commit -m "feat(domain): 实现 Bible 领域模型

- 创建 Character 和 WorldSetting 实体
- 实现 Bible 聚合根
- 支持人物和世界设定管理
- 添加 15 个单元测试"
```

---

### Task 13: 实现 Bible 仓储

**目标：** 实现 Bible 持久化

**文件：**
- 创建：`infrastructure/persistence/mappers/bible_mapper.py`
- 创建：`infrastructure/persistence/repositories/file_bible_repository.py`
- 创建：`tests/integration/infrastructure/persistence/repositories/test_file_bible_repository.py`

**步骤：**

1. 实现 BibleMapper
2. 实现 FileBibleRepository
3. 编写集成测试（6 个测试）
4. 提交

---

### Task 14: 实现 AI 生成服务

**目标：** 创建 AI 生成应用服务

**文件：**
- 创建：`application/services/ai_generation_service.py`
- 创建：`tests/unit/application/services/test_ai_generation_service.py`

**步骤：**

1. 实现 AIGenerationService
```python
class AIGenerationService:
    def __init__(
        self,
        llm_service: LLMService,
        novel_repository: NovelRepository,
        bible_repository: BibleRepository
    ):
        self.llm_service = llm_service
        self.novel_repository = novel_repository
        self.bible_repository = bible_repository

    async def generate_chapter(
        self,
        novel_id: str,
        chapter_number: int,
        outline: str
    ) -> str:
        """生成章节内容"""
        # 1. 获取小说和 Bible
        novel = self.novel_repository.get_by_id(NovelId(novel_id))
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))

        # 2. 构建提示词
        prompt = self._build_chapter_prompt(novel, bible, chapter_number, outline)

        # 3. 调用 LLM
        result = await self.llm_service.generate(prompt)

        return result.content

    def _build_chapter_prompt(self, novel, bible, chapter_number, outline) -> Prompt:
        # 构建提示词
```

2. 编写单元测试（5 个测试）

3. 提交
```bash
git commit -m "feat(application): 实现 AI 生成服务

- 创建 AIGenerationService
- 支持章节内容生成
- 集成 Novel 和 Bible 上下文
- 添加 5 个单元测试"
```

---

### Task 15: 扩展应用层服务

**目标：** 扩展 NovelService，添加更多用例

**文件：**
- 修改：`application/services/novel_service.py`
- 创建：`application/services/chapter_service.py`
- 创建：`application/services/bible_service.py`

**步骤：**

1. 扩展 NovelService
```python
def update_novel_stage(self, novel_id: str, stage: str) -> NovelDTO:
    """更新小说阶段"""

def get_novel_statistics(self, novel_id: str) -> Dict[str, Any]:
    """获取小说统计信息"""
```

2. 创建 ChapterService
```python
class ChapterService:
    def update_chapter_content(
        self,
        chapter_id: str,
        content: str
    ) -> ChapterDTO:
        """更新章节内容"""

    def list_chapters_by_novel(self, novel_id: str) -> List[ChapterDTO]:
        """列出小说的所有章节"""
```

3. 创建 BibleService
```python
class BibleService:
    def add_character(
        self,
        novel_id: str,
        character_id: str,
        name: str,
        description: str
    ) -> BibleDTO:
        """添加人物"""

    def add_world_setting(
        self,
        novel_id: str,
        setting_id: str,
        name: str,
        description: str,
        setting_type: str
    ) -> BibleDTO:
        """添加世界设定"""
```

4. 编写单元测试（10 个测试）

5. 提交
```bash
git commit -m "feat(application): 扩展应用层服务

- 扩展 NovelService 功能
- 创建 ChapterService
- 创建 BibleService
- 添加 10 个单元测试"
```

---

## 第二阶段任务（Day 8-14）

### Task 16: 创建新的 API 路由层

**目标：** 创建新的 FastAPI 路由，替代旧的 web/app.py

**文件：**
- 创建：`interfaces/__init__.py`
- 创建：`interfaces/api/__init__.py`
- 创建：`interfaces/api/v1/__init__.py`
- 创建：`interfaces/api/v1/novels.py`
- 创建：`interfaces/api/v1/chapters.py`
- 创建：`interfaces/api/v1/bible.py`
- 创建：`interfaces/api/v1/ai.py`
- 创建：`interfaces/api/dependencies.py`
- 创建：`interfaces/main.py`

**步骤：**

1. 创建依赖注入配置
```python
# interfaces/api/dependencies.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    # Storage
    storage = providers.Singleton(
        FileStorage,
        base_path=Path("./data")
    )

    # Repositories
    novel_repository = providers.Factory(
        FileNovelRepository,
        storage=storage
    )

    chapter_repository = providers.Factory(
        FileChapterRepository,
        storage=storage
    )

    # Services
    novel_service = providers.Factory(
        NovelService,
        novel_repository=novel_repository
    )
```

2. 创建 novels 路由
```python
# interfaces/api/v1/novels.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/novels", tags=["novels"])

@router.post("/", response_model=NovelDTO)
async def create_novel(
    request: CreateNovelRequest,
    service: NovelService = Depends(get_novel_service)
):
    return service.create_novel(
        novel_id=request.id,
        title=request.title,
        author=request.author,
        target_chapters=request.target_chapters
    )

@router.get("/{novel_id}", response_model=NovelDTO)
async def get_novel(
    novel_id: str,
    service: NovelService = Depends(get_novel_service)
):
    novel = service.get_novel(novel_id)
    if novel is None:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel

@router.get("/", response_model=List[NovelDTO])
async def list_novels(
    service: NovelService = Depends(get_novel_service)
):
    return service.list_novels()

@router.delete("/{novel_id}")
async def delete_novel(
    novel_id: str,
    service: NovelService = Depends(get_novel_service)
):
    service.delete_novel(novel_id)
    return {"message": "Novel deleted"}
```

3. 创建 chapters 路由
4. 创建 bible 路由
5. 创建 ai 路由
6. 创建主应用

```python
# interfaces/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="aitext API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(novels_router, prefix="/api/v1")
app.include_router(chapters_router, prefix="/api/v1")
app.include_router(bible_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
```

7. 提交
```bash
git commit -m "feat(interfaces): 创建新的 API 路由层

- 实现依赖注入容器
- 创建 RESTful API 路由
- 支持 novels, chapters, bible, ai 端点
- 使用 FastAPI 最佳实践"
```

---

### Task 17: 迁移 pipeline 功能

**目标：** 将 pipeline/runner.py 迁移到新架构

**文件：**
- 创建：`application/workflows/__init__.py`
- 创建：`application/workflows/novel_generation_workflow.py`
- 删除：`pipeline/runner.py`
- 删除：`pipeline/confirm.py`

**步骤：**

1. 分析 pipeline/runner.py 功能
```bash
# 查看 pipeline/runner.py 的主要功能
cat pipeline/runner.py | grep "def " | head -20
```

2. 创建 NovelGenerationWorkflow
```python
class NovelGenerationWorkflow:
    def __init__(
        self,
        novel_service: NovelService,
        chapter_service: ChapterService,
        ai_generation_service: AIGenerationService
    ):
        self.novel_service = novel_service
        self.chapter_service = chapter_service
        self.ai_generation_service = ai_generation_service

    async def run_full_generation(
        self,
        novel_id: str,
        target_chapters: int
    ) -> NovelDTO:
        """运行完整的小说生成流程"""
        # 1. 创建小说
        # 2. 生成大纲
        # 3. 逐章生成
        # 4. 返回结果
```

3. 删除旧 pipeline 代码
```bash
git rm -r pipeline/
```

4. 提交
```bash
git commit -m "refactor: 迁移 pipeline 到新架构

- 创建 NovelGenerationWorkflow
- 使用新的应用层服务
- 删除旧的 pipeline/ 目录"
```

---

### Task 18: 清理旧 web 代码

**目标：** 删除旧的 web/ 目录，完全使用新 API

**文件：**
- 删除：`web/app.py`
- 删除：`web/` 下所有旧文件
- 保留：`web/middleware/` 中可复用的中间件

**步骤：**

1. 检查 web/ 中是否有可复用代码
```bash
# 查看中间件
ls -la web/middleware/
```

2. 迁移可复用的中间件到 interfaces/
```bash
# 如果有用的中间件，迁移到新位置
cp web/middleware/error_handler.py interfaces/api/middleware/
```

3. 删除旧 web 代码
```bash
git rm web/app.py
git rm web/cast_*.py
git rm web/chat_*.py
git rm web/desk.py
git rm web/graph_*.py
git rm web/jobs.py
git rm web/log_stream.py
git rm -r web/models/
git rm -r web/repositories/
```

4. 提交
```bash
git commit -m "refactor: 清理旧 web 代码

- 删除旧的 web/app.py 和相关文件
- 迁移可复用中间件到新位置
- 完全使用新的 DDD 架构"
```

---

### Task 19: 前端 API 适配

**目标：** 更新前端 API 调用，适配新的 RESTful API

**文件：**
- 修改：`web-app/src/api/book.ts`
- 修改：`web-app/src/api/chapter.ts`
- 创建：`web-app/src/api/bible.ts`
- 创建：`web-app/src/api/ai.ts`

**步骤：**

1. 更新 API 基础 URL
```typescript
// web-app/src/api/config.ts
export const API_BASE_URL = 'http://localhost:8000/api/v1'
```

2. 更新 book.ts
```typescript
// 旧: GET /api/books
// 新: GET /api/v1/novels
export async function listNovels(): Promise<NovelDTO[]> {
  const response = await axios.get(`${API_BASE_URL}/novels`)
  return response.data
}
```

3. 更新 chapter.ts
4. 创建 bible.ts
5. 创建 ai.ts

6. 提交
```bash
git commit -m "refactor(frontend): 适配新的 RESTful API

- 更新 API 调用路径
- 使用新的 DTO 类型
- 添加 Bible 和 AI API 调用"
```

---

### Task 20: 集成测试和文档

**目标：** 编写完整的集成测试，更新文档

**文件：**
- 创建：`tests/integration/test_api_endpoints.py`
- 创建：`docs/week2-3-summary.md`
- 更新：`README.md`

**步骤：**

1. 编写 API 集成测试
```python
from fastapi.testclient import TestClient

def test_create_and_get_novel(client: TestClient):
    # 创建小说
    response = client.post("/api/v1/novels", json={
        "id": "test-novel",
        "title": "测试小说",
        "author": "测试作者",
        "target_chapters": 10
    })
    assert response.status_code == 200

    # 获取小说
    response = client.get("/api/v1/novels/test-novel")
    assert response.status_code == 200
    assert response.json()["title"] == "测试小说"
```

2. 运行所有测试
```bash
pytest tests/ -v --cov=domain --cov=infrastructure --cov=application --cov=interfaces
```

3. 创建 Week 2-3 总结文档

4. 更新 README.md
```markdown
## 快速开始

### 后端
```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务器
python -m interfaces.main
```

### 前端
```bash
cd web-app
npm install
npm run dev
```
```

5. 提交
```bash
git commit -m "docs: 完成 Week 2-3 集成测试和文档

- 添加 API 集成测试
- 创建 Week 2-3 总结文档
- 更新 README.md
- 验证测试覆盖率 > 80%"
```

---

## 清理检查清单

### 需要删除的旧代码
- [ ] `web/app.py` (745 行，已被新 API 替代)
- [ ] `web/cast_*.py` (人物相关，迁移到 Bible 领域)
- [ ] `web/chat_*.py` (对话相关，迁移到 AI 服务)
- [ ] `web/desk.py` (工作台，前端处理)
- [ ] `web/graph_*.py` (图谱工具，迁移到 Bible 服务)
- [ ] `web/jobs.py` (后台任务，迁移到 Workflow)
- [ ] `web/log_stream.py` (日志流，使用标准日志)
- [ ] `web/models/` (旧模型，使用新 DTO)
- [ ] `web/repositories/` (旧仓储，使用新仓储)
- [ ] `pipeline/runner.py` (流水线，迁移到 Workflow)
- [ ] `pipeline/confirm.py` (确认工具，不再需要)

### 需要保留的代码
- [ ] `web/middleware/error_handler.py` (迁移到 interfaces/)
- [ ] `web/middleware/logging_config.py` (迁移到 interfaces/)

---

## 测试目标

### 覆盖率目标
- 领域层: > 90%
- 应用层: > 85%
- 基础设施层: > 80%
- 接口层: > 75%
- 总体: > 80%

### 测试数量预估
- Week 1: 129 个测试
- Week 2-3 新增: ~80 个测试
- 总计: ~210 个测试

---

## 风险和注意事项

1. **API 兼容性**
   - 前端需要同步更新
   - 考虑提供 API 版本控制

2. **数据迁移**
   - 旧数据格式可能需要迁移脚本
   - 建议先在测试环境验证

3. **性能考虑**
   - 新架构可能有性能差异
   - 需要进行性能测试

4. **渐进式迁移**
   - 可以先保留旧 API，逐步切换
   - 确保前端稳定后再删除旧代码

---

## 总结

Week 2-3 合并计划将：
1. 扩展 DDD 架构功能（Chapter、Bible、AI 服务）
2. 创建新的 RESTful API 层
3. 迁移旧代码到新架构
4. 清理无用代码
5. 前端适配新 API
6. 完整的测试和文档

预计完成后：
- 代码库更清晰（删除 ~3000 行旧代码）
- 架构更合理（完整的 DDD 分层）
- 测试更完善（~210 个测试）
- 维护更容易（职责清晰）
