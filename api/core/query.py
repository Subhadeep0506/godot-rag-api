import api.config.constant as constant

from fastapi import HTTPException
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    HumanMessagePromptTemplate,
)
from langgraph.graph import START, StateGraph, END
import api.config.constant as constant
from api.config.state import State
from api.core.tools import *
from api.schema.ai_state import AIState
from api.models.chat_session import ChatSession


class Query:
    def __init__(self):
        self.prompt = None
        self.reddit_prompt = None

        self.__initialize_query_pipeline()
        self.__initialize_reddit_query_pipeline()

    def __initialize_query_pipeline(
        self,
    ):
        try:
            self.prompt = ChatPromptTemplate(
                messages=[
                    HumanMessagePromptTemplate(
                        prompt=PromptTemplate(
                            input_variables=["chat_history", "context", "question"],
                            template=constant.SYSTEM_PROMPT,
                        ),
                    )
                ],
            )
        except Exception as e:
            State.logger.error(f"Error initializing query pipeline: {e}")
            raise Exception(f"Error initializing query pipeline: {e}")

    def __initialize_reddit_query_pipeline(self):
        try:
            self.reddit_prompt = ChatPromptTemplate(
                messages=[
                    HumanMessagePromptTemplate(
                        prompt=PromptTemplate(
                            input_variables=["chat_history", "context", "question"],
                            template=constant.REDDIT_SYSTEM_PROMPT,
                        ),
                    )
                ],
            )
        except Exception as e:
            State.logger.error(f"Error initializing Reddit query pipeline: {e}")
            raise Exception(f"Error initializing Reddit query pipeline: {e}")

    def __flatten_sources(self, sources: List[Document]) -> List[Dict]:
        final_sources = []
        for source in sources:
            src = source.metadata.get("source", "Unknown Source")
            contents = source.page_content
            final_sources.append(
                {
                    "source": src,
                    "content": contents,
                }
            )
        return final_sources

    def __flatten_reddit_sources(self, sources: List[Document]) -> List[Dict]:
        final_sources = []
        for source in sources:
            src = source.metadata.get("author", "Unknown Author")
            contents = source.page_content
            final_sources.append(
                {
                    "author": src,
                    "content": contents,
                }
            )
        return final_sources

    def generate_response(
        self,
        query: str,
        category: str = None,
        sub_category: str = None,
        top_k: int = 4,
        temperature: float = 0.0,
        session_id: str = None,
        model_name: str = None,
        memory_service: str = "astradb",
        db=None,
    ):
        try:
            session = db.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                raise HTTPException(
                    status_code=404, detail=f"Session with id {session_id} not found."
                )
            graph_builder = StateGraph(AIState).add_sequence(
                [retrieve, generate, add_message_history]
            )
            graph_builder.add_edge(START, "retrieve")
            graph_builder.add_edge("retrieve", "generate")
            graph_builder.add_edge("generate", "add_message_history")
            graph_builder.add_edge("add_message_history", END)
            graph = graph_builder.compile()

            result = graph.invoke(
                {
                    "question": query,
                    "session_id": session_id,
                    "category": category,
                    "sub_category": sub_category,
                    "memory_service": memory_service,
                    "model_name": model_name,
                    "temperature": temperature,
                    "top_k": top_k,
                    "vector_store": State.vector_store,
                    "prompt": self.prompt,
                }
            )

            message = State.message_controller.add_message(
                db=db,
                session_id=session_id,
                content={"question": query, "answer": result["answer"]},
                sources=self.__flatten_sources(sources=result["context"]),
            )

            return message
        except HTTPException:
            raise
        except Exception as e:
            State.logger.error(f"Error in response generation: {e}")
            return {
                "output": f"Error generating response {e}",
                "intermediate_steps": [],
            }

    def generate_reddit_response(
        self,
        query: str,
        username: str,
        top_k: int = 4,
        temperature: float = 0.0,
        relevance: str = "hot",
        memory_service: str = "astradb",
        session_id: str = None,
        model_name: str = None,
        db=None,
    ):
        try:
            session = db.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                raise HTTPException(
                    status_code=404, detail=f"Session with id {session_id} not found."
                )

            graph_builder = StateGraph(AIState).add_sequence(
                [retrieve_with_reddit, generate, add_message_history]
            )
            graph_builder.add_edge(START, "retrieve_with_reddit")
            graph_builder.add_edge("retrieve_with_reddit", "generate")
            graph_builder.add_edge("generate", "add_message_history")
            graph_builder.add_edge("add_message_history", END)
            graph = graph_builder.compile()

            result = graph.invoke(
                {
                    "question": query,
                    "session_id": session_id,
                    "memory_service": memory_service,
                    "reddit_username": username,
                    "reddit_relevance": relevance,
                    "reddit_top_k": top_k,
                    "temperature": temperature,
                    "model_name": model_name,
                    "prompt": self.reddit_prompt,
                }
            )
            message = State.message_controller.add_message(
                db=db,
                session_id=session_id,
                content={"question": query, "answer": result["answer"]},
                sources=self.__flatten_reddit_sources(sources=result["context"]),
            )
            return message
        except HTTPException:
            raise
        except Exception as e:
            State.logger.error(f"Error generating response: {e}")
            return {
                "output": f"Error generating response {e}",
                "intermediate_steps": [],
            }
