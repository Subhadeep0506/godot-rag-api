from api.schema.ai_state import AIState
from api.config.state import State


def add_message_history(state: AIState):
    try:
        memory_instance = state.get("memory_instance")
        memory_instance.add_user_message(state.get("question"))
        memory_instance.add_ai_message(state.get("answer"))
        return state
    except Exception as e:
        State.logger.error(f"[AGENT] Error adding message history: {e}")
        raise Exception(f"[AGENT] Error adding message history: {e}")
