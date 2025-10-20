import sys
from dotenv import load_dotenv

sys.path.append("..")
_ = load_dotenv()

from api.core.infisical import InfisicalManagedCredentials

secrets_client = InfisicalManagedCredentials()

from api.services.embeddings_factory import EmbeddingsFactory
from api.services.vector_store_factory import VectorStoreFactory
from api.services.llm_factory import LLMFactory
from api.core.query import Query


class Orchastrator:
    def __init__(self):
        self.embeddings = EmbeddingsFactory().get_embeddings(
            "sentence-transformers", "intfloat/multilingual-e5-large-instruct"
        )

        self.vector_store = VectorStoreFactory().get_vectorstore(
            vectorstore_service="astradb",
            embeddings=self.embeddings,
        )
        self.query_chain = Query(vectorstore=self.vector_store)

    def generate_response(
        self,
        query: str,
        session_id: str,
        model_name: str,
        category: str,
        sub_category: str,
        top_k: int = 10,
        temperature: float = 0.7,
        memory_service: str = "astradb",
    ):
        self.llm = LLMFactory().get_chat_model(
            model_name=model_name,
            temperature=temperature,
        )
        response = self.query_chain.generate_response(
            query=query,
            category=category,
            sub_category=sub_category,
            source=None,
            top_k=top_k,
            session_id=session_id,
            memory_service=memory_service,
            llm=self.llm,
        )
        return response

    def generate_reddit_response(
        self,
        query: str,
        model_name: str,
        temperature: float,
        username: str,
        relevance: str,
        session_id: str,
        top_k: int = 10,
        memory_service: str = "astradb",
    ):
        self.llm = LLMFactory().get_chat_model(
            model_name=model_name,
            temperature=temperature,
        )
        response = self.query_chain.generate_reddit_response(
            query=query,
            username=username,
            session_id=session_id,
            top_k=top_k,
            relevance=relevance,
            memory_service=memory_service,
            llm=self.llm,
        )
        return response
