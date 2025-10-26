from langchain_core.messages import HumanMessage, AIMessage
from api.schema.ai_state import AIState
from api.services.llm_factory import LLMFactory
from api.services.memory_factory import MemoryFactory
from api.services.reddit import RedditClient
from api.config.state import State


def _parse_and_flatten_memory(messages: list):
    memory_string = ""
    if not messages:
        return memory_string
    for message in messages:
        if type(message) == HumanMessage:
            memory_string += f"Human: {message.content}\n"
        elif type(message) == AIMessage:
            memory_string += f"Assistant: {message.content}\n\n"
    return memory_string


def retrieve(state: AIState):
    try:
        filters = {
            "category": state.get("category"),
            "sub_category": state.get("sub_category"),
        }
        clean_filter = {k: v for k, v in filters.items() if v}
        retrieved_docs = (
            state.get("vector_store")
            .as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": state.get("top_k"),
                    "filter": clean_filter,
                },
            )
            .get_relevant_documents(
                query=state["question"],
            )
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
        state["model"] = model
        state["memory_instance"] = memory_instance
        state["chat_history"] = chat_history
        state["context"] = retrieved_docs
        return state
    except Exception as e:
        State.logger.error(f"Error in retrieval: {e}")
        raise Exception(f"Error in retrieval: {e}")


def retrieve_with_reddit(state: AIState):
    try:
        user_agent = f"extractor by {state.get('username')}"
        reddit_loader = RedditClient(
            user_agent=user_agent,
        )
        reddit_retriever = reddit_loader.as_retriever(
            k=state.get("reddit_top_k"), relevance=state.get("reddit_relevance")
        )

        retrieved_docs = reddit_retriever._get_relevant_documents(
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
        state["reddit_retriever"] = reddit_retriever
        state["reddit_loader"] = reddit_loader
        state["model"] = model
        state["memory_instance"] = memory_instance
        state["chat_history"] = chat_history
        state["context"] = retrieved_docs
        return state
    except Exception as e:
        State.logger.error(f"[AGENT] Error in Reddit retrieval: {e}")
        raise Exception(f"[AGENT] Error in Reddit retrieval: {e}")
