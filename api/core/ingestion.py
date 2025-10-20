from typing import List

from api.utils.rtd_reader import ReadTheDocsReader
from api.utils.parqet_reader import ConversationsReader
from tqdm import tqdm
from langchain.vectorstores.base import VectorStore
from api.services.logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class Ingestion:
    def __init__(self, vectorstore: VectorStore):
        self.rtd_loader = ReadTheDocsReader()
        self.conversationds_loader = ConversationsReader()
        self.vectorstore = vectorstore

    def ingest_docs(self, directory: str):
        try:
            logger.info(f"Starting ingestion from {directory}")
            docs = self.rtd_loader.load(directory=directory)[8900:]
            chunk_size = 100
            total = len(docs)
            logger.info(f"Loaded {total} documents from {directory}")
            total_chunks = (total + chunk_size - 1) // chunk_size
            with tqdm(
                total=total_chunks,
                desc="Ingesting documents in 100 chunk sizes...",
                unit="chunk",
            ) as pbar:
                for i in range(0, total, chunk_size):
                    chunk = docs[i : i + chunk_size]
                    _ = self.vectorstore.add_documents(
                        documents=chunk,
                    )
                    pbar.update(1)
                    logger.info(f"Ingested {i+chunk_size}/{total} chunks.")
            logger.info(
                f"Finished ingestion from {directory}, ingested {total} documents."
            )
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")

    def ingest_conversations(self, dataset_name: str):
        try:
            docs = self.conversationds_loader.load(dataset_name=dataset_name)
            total = len(docs)
            chunk_size = 100
            logger.info(f"Loaded conversations from {dataset_name}")

            total_chunks = (total + chunk_size - 1) // chunk_size
            with tqdm(
                total=total_chunks,
                desc="Ingesting conversations in 100 chunk sizes...",
                unit="chunk",
            ) as pbar:
                for i in range(0, total, chunk_size):
                    chunk = docs[i : i + chunk_size]
                    _ = self.vectorstore.add_documents(
                        documents=chunk,
                    )
                    pbar.update(1)
                    logger.info(f"Ingested {i+chunk_size}/{total} chunks.")
            logger.info(
                f"Finished ingestion of {dataset_name}, ingested {total} Conversations."
            )
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
