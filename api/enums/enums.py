from enum import Enum


class EmbeddingsService(Enum):
    COHERE = "cohere"
    SENTENCE_TRANSFORMERS = "sentence-transformers"


class LLMService(Enum):
    COHERE = "cohere"
    GEMINI = "gemini"
    GROQ = "groq"
    MISTRAL = "mistral"


class VectorStoreService(Enum):
    MILVUS = "milvus"
    ASTRADB = "astradb"


class MemoryService(Enum):
    UPSTASH = "upstash"
    ASTRADB = "astradb"