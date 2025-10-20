import api.config.constant as constant

from langchain_astradb import AstraDBVectorStore
from langchain_milvus import Milvus
from typing import Union, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from api.services.logger_service import LoggerService
from api.services.memory_factory import MemoryFactory
from api.services.llm_factory import ChatCohere, ChatGoogleGenerativeAI
from api.services.reddit import RedditClient


logger = LoggerService.get_logger(__name__)


class Query:
    def __init__(self, vectorstore: Union[AstraDBVectorStore, Milvus]):
        self.vectorstore = vectorstore
        self.vectorstore_retriever = None
        self.reddit_retriever = None
        self.memory = None
        self.reddit_loader = None
        self.username = None

    def __initialize_query_pipeline(
        self,
        filter: Dict[str, str] = None,
        top_k: int = 4,
        session_id: str = None,
        memory_service: str = None,
    ):
        try:
            self.vectorstore_retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": top_k,
                    "filter": filter,
                },
            )
            self.memory = MemoryFactory.get_memory_instance(
                memory_service=memory_service,
                session_id=session_id,
            )
            tools = [
                create_retriever_tool(
                    retriever=self.vectorstore_retriever,
                    name="Retrieval_QA",
                    description="Retrieves relevant documents from the vector store.",
                )
            ]
            return tools
        except Exception as e:
            logger.error(f"Error initializing query pipeline: {e}")
            return []

    def __initialize_reddit_query_pipeline(
        self,
        username: str,
        k: int = 5,
        relevance: str = "hot",
        session_id: str = None,
        memory_service: str = None,
    ):
        try:
            if self.reddit_loader is None:
                user_agent = f"extractor by {username}"
                self.reddit_loader = RedditClient(
                    user_agent=user_agent,
                )
            elif self.username and self.username != username:
                user_agent = f"extractor by {username}"
                self.reddit_loader = RedditClient(
                    user_agent=user_agent,
                )
            self.reddit_retriever = self.reddit_loader.as_retriever(
                k=k, relevance=relevance
            )
            self.memory = MemoryFactory.get_memory_instance(
                memory_service=memory_service,
                session_id=session_id,
            )
            tools = [
                create_retriever_tool(
                    retriever=self.reddit_retriever,
                    name="Reddit_QA",
                    description="Retrieves relevant threads from Godot and Gamedev subreddit.",
                )
            ]
            return tools
        except Exception as e:
            logger.error(f"Error initializing Reddit query pipeline: {e}")
            return []

    def __get_message_history(self):
        messages = self.memory.messages[-4:] if self.memory.messages else []
        return messages

    def __add_message_history(
        self,
        query: str,
        response: str,
    ) -> None:
        self.memory.add_user_message(query)
        self.memory.add_ai_message(response)

    def generate_response(
        self,
        query: str,
        category: str = None,
        sub_category: str = None,
        source: str = None,
        top_k: int = 4,
        session_id: str = None,
        memory_service: str = None,
        llm: Union[ChatCohere, ChatGoogleGenerativeAI] = None,
    ):
        try:
            filter = {
                "category": category,
                "sub_category": sub_category,
                "source": source,
            }
            clean_filter = {k: v for k, v in filter.items() if v}
            tools = self.__initialize_query_pipeline(
                filter=clean_filter,
                top_k=top_k,
                session_id=session_id,
                memory_service=memory_service,
            )
            history_messages = self.__get_message_history()
            PROMPT = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=constant.SYSTEM_PROMPT),
                    *history_messages,
                    HumanMessage(content=query),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=PROMPT)
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
            )
            response = agent_executor.invoke(
                input={
                    "input": query,
                },
                return_only_outputs=True,
            )
            self.__add_message_history(query=query, response=response["output"])
            return response
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            return {
                "output": f"Error generating response {e}",
                "intermediate_steps": [],
            }

    def generate_reddit_response(
        self,
        query: str,
        username: str,
        top_k: int = 4,
        relevance: str = "hot",
        session_id: str = None,
        memory_service: str = None,
        llm: Union[ChatCohere, ChatGoogleGenerativeAI] = None,
    ):
        try:
            tools = self.__initialize_reddit_query_pipeline(
                username=username,
                k=top_k,
                relevance=relevance,
                session_id=session_id,
                memory_service=memory_service,
            )
            history_messages = self.__get_message_history()
            PROMPT = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=constant.REDDIT_SYSTEM_PROMPT),
                    *history_messages,
                    HumanMessage(content=query),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
            agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=PROMPT)
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=False,
                handle_parsing_errors=True,
                return_intermediate_steps=True,
            )
            response = agent_executor.invoke(
                input={
                    "input": query,
                },
                return_only_outputs=True,
            )
            self.__add_message_history(query=query, response=response["output"])
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "output": f"Error generating response {e}",
                "intermediate_steps": [],
            }
