"""向量检索门面，隔离异步调用"""
import asyncio
from typing import List, Optional

from domain.ai.services.vector_store import VectorStore
from domain.ai.services.embedding_service import EmbeddingService


class VectorRetrievalFacade:
    """向量检索门面

    提供同步接口，内部使用 asyncio 隔离异步调用，避免全栈 async 改造。
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def sync_search(
        self,
        collection: str,
        query_text: str,
        limit: int = 5,
    ) -> List[dict]:
        """同步搜索接口

        Args:
            collection: 集合名称
            query_text: 查询文本
            limit: 返回结果数量

        Returns:
            相似向量列表，每个元素包含 id, score, payload
        """
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 运行异步搜索
        return loop.run_until_complete(
            self._async_search(collection, query_text, limit)
        )

    async def _async_search(
        self,
        collection: str,
        query_text: str,
        limit: int,
    ) -> List[dict]:
        """内部异步搜索实现"""
        # 生成查询向量
        query_vector = await self.embedding_service.embed(query_text)

        # 执行向量搜索
        results = await self.vector_store.search(
            collection=collection,
            query_vector=query_vector,
            limit=limit,
        )

        return results
