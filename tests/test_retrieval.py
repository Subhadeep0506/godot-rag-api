import sys

sys.path.append("..")

from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

from src.core.infisical import InfisicalManagedCredentials

secrets_client = InfisicalManagedCredentials()

from src.core.ingestion import Ingestion
from src.services.embeddings_factory import EmbeddingsFactory
from src.services.vector_store_factory import VectorStoreFactory
import praw

embeddings = EmbeddingsFactory().get_embeddings(
    "sentence-transformers", "intfloat/multilingual-e5-large-instruct"
)

vector_store = VectorStoreFactory().get_vectorstore(
    vectorstore_service="astradb",
    embeddings=embeddings,
)

filter = {
    "category": "getting_started",
    "sub_category": None,
    "source": None,
}
clean_filter = {k: v for k, v in filter.items() if v}

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 10,
        "filter": clean_filter,
    },
)

res = retriever.get_relevant_documents(
    query="How to use the new animation system in Godot 4.0?"
)
print(res)
