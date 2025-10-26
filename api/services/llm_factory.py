import os
from typing import Union

from langchain_cohere.chat_models import ChatCohere
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_groq.chat_models import ChatGroq

from ..enums.enums import LLMService
from api.config.state import State


class LLMFactory:
    @staticmethod
    def get_chat_model(
        model_name: str,
        temperature: float = 0.7,
    ) -> Union[ChatCohere, ChatGoogleGenerativeAI, ChatMistralAI, ChatGroq]:
        if "gemini" in model_name:
            llm_service = LLMService.GEMINI.value
        elif "command" in model_name:
            llm_service = LLMService.COHERE.value
        elif any(
            model in model_name.lower()
            for model in ["mistral", "ministral", "codestral"]
        ):
            llm_service = LLMService.MISTRAL.value
        elif any(model in model_name.lower() for model in ["llama", "gemma2", "qwen"]):
            llm_service = LLMService.GROQ.value

        if llm_service == LLMService.COHERE.value:
            State.logger.info("Using Cohere chat model.")
            return ChatCohere(
                model=model_name,
                temperature=temperature,
                cohere_api_key=os.environ["COHERE_API_KEY"],
            )
        elif llm_service == LLMService.GEMINI.value:
            State.logger.info("Using Gemini chat model.")
            return ChatGoogleGenerativeAI(
                model=model_name,
                api_key=os.environ["GEMINI_API_KEY"],
                disable_streaming=True,
                temperature=temperature,
            )
        elif llm_service == LLMService.MISTRAL.value:
            State.logger.info("Using Mistral chat model.")
            return ChatMistralAI(
                model=model_name,
                api_key=os.environ["MISTRAL_API_KEY"],
                temperature=temperature,
            )
        elif llm_service == LLMService.GROQ.value:
            State.logger.info("Using Groq chat model.")
            return ChatGroq(
                model=model_name,
                api_key=os.environ["GROQ_API_KEY"],
                temperature=temperature,
            )
        else:
            raise ValueError("Unsupported chat service.")
