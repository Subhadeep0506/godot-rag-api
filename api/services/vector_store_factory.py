import os
from typing import Union

from langchain_milvus.vectorstores import Milvus
from langchain_postgres.vectorstores import PGVector
from langchain_astradb import AstraDBVectorStore
from pymilvus import DataType, MilvusClient

from ..enums.enums import VectorStoreService
from .logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class VectorStoreFactory:
    @staticmethod
    def get_vectorstore(
        vectorstore_service: str,
        embeddings,
    ) -> Union[AstraDBVectorStore, Milvus]:
        if vectorstore_service == VectorStoreService.ASTRADB.value:
            logger.info("Using AstraDB")
            try:
                return AstraDBVectorStore(
                    collection_name=os.environ["ASTRADB_COLLECTION_NAME"],
                    embedding=embeddings,
                    api_endpoint=os.environ["ASTRA_URI"],
                    token=os.environ["ASTRA_TOKEN"],
                )
            except Exception as e:
                logger.error("Error connecting to AstraDB: %s", e)
        elif vectorstore_service == VectorStoreService.MILVUS.value:
            logger.info("Using Milvus")
            client = MilvusClient(
                uri=os.environ["MILVUS_DATABASE_URI"],
                token=os.environ["MILVUS_ACCESS_TOKEN"],
            )
            if not client.has_collection(os.environ["MILVUS_COLLECTION_NAME"]):
                logger.info("Creating Milvus collection")
                try:
                    schema = client.create_schema(
                        enable_dynamic_field=True, description=""
                    )
                    schema.add_field(
                        field_name="id",
                        datatype=DataType.VARCHAR,
                        max_length=65535,
                        description="The Primary Key",
                        is_primary=True,
                        auto_id=False,
                    )
                    schema.add_field(
                        field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024
                    )
                    schema.add_field(field_name="metadata", datatype=DataType.JSON)
                    schema.add_field(
                        field_name="document",
                        datatype=DataType.VARCHAR,
                        max_length=65535,
                    )
                    index_params = client.prepare_index_params()
                    index_params.add_index(
                        field_name="vector",
                        metric_type="COSINE",
                        index_type="AUTOINDEX",
                    )
                    client.create_collection(
                        collection_name=os.environ["MILVUS_COLLECTION_NAME"],
                        schema=schema,
                        index_params=index_params,
                    )
                except Exception as e:
                    logger.error("Error creating Milvus collection: %s", e)
            return Milvus(
                embedding_function=embeddings,
                collection_name=os.environ["MILVUS_COLLECTION_NAME"],
                connection_args={
                    "uri": os.environ["MILVUS_DATABASE_URI"],
                    "token": os.environ["MILVUS_ACCESS_TOKEN"],
                },
                auto_id=False,
                primary_field="id",
                text_field="document",
                metadata_field="metadata",
                vector_field="vector",
            )
        else:
            raise ValueError("Unsupported vectorstore service")
