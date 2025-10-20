import os
from typing import Union
from langchain.memory.chat_message_histories.upstash_redis import (
    UpstashRedisChatMessageHistory,
)
from langchain_astradb.chat_message_histories import AstraDBChatMessageHistory
from ..enums.enums import MemoryService
from .logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class MemoryFactory:
    @staticmethod
    def get_memory_instance(
        memory_service: str,
        session_id: str,
    ) -> Union[UpstashRedisChatMessageHistory, AstraDBChatMessageHistory]:
        if memory_service == MemoryService.UPSTASH.value:
            logger.info("Using Upstash Redis memory service.")
            return UpstashRedisChatMessageHistory(
                session_id=session_id,
                url=os.getenv("UPSTASH_REDIS_URL"),
                token=os.getenv("UPSTASH_REDIS_TOKEN"),
            )
        elif memory_service == MemoryService.ASTRADB.value:
            logger.info("Using AstraDB memory service.")
            return AstraDBChatMessageHistory(
                session_id=session_id,
                collection_name="chat_history",
                token=os.environ["ASTRA_TOKEN"],
                api_endpoint=os.environ["ASTRA_URI"],
            )
        else:
            raise ValueError("Unsupported memory service.")
