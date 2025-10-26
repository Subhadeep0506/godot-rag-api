from api.schema.ai_state import AIState
from api.config.state import State


def generate(state: AIState):
    try:
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        model = state.get("model")
        messages = state.get("prompt").invoke(
            {
                "question": state["question"],
                "context": docs_content,
                "chat_history": state["chat_history"],
            }
        )
        response = model.invoke(messages)
        state["answer"] = response.content
        return state
    except Exception as e:
        State.logger.error(f"[AGENT] Error in generation: {e}")
        raise Exception(f"[AGENT] Error in generation: {e}")
