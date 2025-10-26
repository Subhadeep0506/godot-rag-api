from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from typing import Union
from langchain_cohere.chat_models import ChatCohere
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq.chat_models import ChatGroq
from langchain.memory.chat_message_histories.upstash_redis import (
    UpstashRedisChatMessageHistory,
)
from langchain_astradb.chat_message_histories import AstraDBChatMessageHistory
from langchain_milvus.vectorstores import Milvus
from langchain_astradb import AstraDBVectorStore
from langchain_core.prompts import ChatPromptTemplate

from api.services.reddit import RedditClient, RedditRetriever


class AIState(TypedDict):
    question: str
    context: List[Document]
    chat_history: str
    answer: str
    session_id: str
    category: str
    sub_category: str
    source: str
    memory_service: str
    model_name: str
    temperature: float
    top_k: int
    model: Union[ChatCohere, ChatGoogleGenerativeAI, ChatMistralAI, ChatGroq]
    memory_instance: Union[UpstashRedisChatMessageHistory, AstraDBChatMessageHistory]
    vector_store: Union[AstraDBVectorStore, Milvus]
    prompt: ChatPromptTemplate

    reddit_username: str
    reddit_relevance: str
    reddit_top_k: int
    reddit_loader: RedditClient
    reddit_retriever: RedditRetriever
