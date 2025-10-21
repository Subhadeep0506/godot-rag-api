from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
)
from typing import Union

from langchain_cohere.chat_models import ChatCohere
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory.chat_message_histories.upstash_redis import (
    UpstashRedisChatMessageHistory,
)
from langchain_astradb.chat_message_histories import AstraDBChatMessageHistory
from api.schema.ai_state import State


def _parse_and_flatten_memory(messages: list):
    memory_string = ""
    for message in messages:
        if type(message) == HumanMessage:
            memory_string += f"Human: {message.content}\n"
        elif type(message) == AIMessage:
            memory_string += f"Assistant: {message.content}\n\n"
    return memory_string


def retrieve(state: State):
    filters = {
        "category": state.get("category"),
        "sub_category": state.get("sub_category"),
    }
    clean_filter = {k: v for k, v in filters.items() if v}
    retrieved_docs = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": state.get("top_k"),
            "filter": clean_filter,
        },
    ).get_relevant_documents(
        query=state["question"],
    )

    memory_instance = MemoryFactory().get_memory_instance(
        memory_service=state.get("memory_service"),
        session_id=state.get("session_id"),
    )

    chat_history = _parse_and_flatten_memory(memory_instance.messages)
    model = LLMFactory.get_chat_model(
        model_name=state.get("model_name"),
        temperature=state.get("temperature", 0.0),
    )
    return {
        "context": retrieved_docs,
        "chat_history": chat_history,
        "model": model,
        "memory_instance": memory_instance,
    }
