import sys

sys.path.append("..")
from dotenv import load_dotenv

_ = load_dotenv()

from src.core.infisical import InfisicalManagedCredentials

secrets_client = InfisicalManagedCredentials()

from src.core.query import Query
from src.services.embeddings_factory import EmbeddingsFactory
from src.services.vector_store_factory import VectorStoreFactory
from src.services.llm_factory import LLMFactory


embeddings = EmbeddingsFactory().get_embeddings(
    "sentence-transformers", "intfloat/multilingual-e5-large-instruct"
)

vector_store = VectorStoreFactory().get_vectorstore(
    vectorstore_service="astradb",
    embeddings=embeddings,
)
llm = LLMFactory().get_chat_model(
    model_name="command-a-03-2025",
)

query = Query(vectorstore=vector_store)

response = query.generate_response(
    query="Can you make it step-wise only? Don't format it into sub steps.",  # "How do I create a 2D tileset?",
    category="tutorials",
    sub_category="2d",
    source=None,
    top_k=10,
    session_id="2893748923647829",
    memory_service="astradb",
    llm=llm,
)
