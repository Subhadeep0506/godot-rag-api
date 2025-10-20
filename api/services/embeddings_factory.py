import os
from typing import Union

import torch
from  langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_cohere.embeddings import CohereEmbeddings
from ..enums.enums import EmbeddingsService
from .logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class EmbeddingsFactory:
    @staticmethod
    def get_embeddings(
        embeddings_service: str,
        model_id: str = None,
    ) -> Union[CohereEmbeddings, SentenceTransformerEmbeddings]:
        if embeddings_service == EmbeddingsService.COHERE.value:
            logger.info("Using Cohere embeddings model.")
            return CohereEmbeddings(
                model=os.environ["COHERE_EMBEDDING_MODEL_NAME"],
                cohere_api_key=os.environ["COHERE_API_KEY"],
            )
        elif embeddings_service == EmbeddingsService.SENTENCE_TRANSFORMERS.value:
            logger.info("Using Sentence Transformers embeddings model.")
            if model_id is not None:
                return SentenceTransformerEmbeddings(
                    model_name=model_id,
                    model_kwargs={  
                        "device": torch.device(
                            "cuda" if torch.cuda.is_available() else "cpu"
                        )
                    },
                )
            else:
                raise ValueError("Model is required for SentenceTransformerEmbeddings")
