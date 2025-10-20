from datasets import load_dataset
from typing import List
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from api.services.logger_service import LoggerService
import hashlib
logger = LoggerService.get_logger(__name__)


class ConversationsReader:
    def __init__(self):
        self.loader = None
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
        )
        logger.info("ReadTheDocsReader initialized.")

    def load(self, dataset_name: str):
        try:
            data = load_dataset(dataset_name, split="train").to_pandas()
            docs: List[Document] = []
            for _, row in data.iterrows():
                message = "\n".join(
                    f"# {key}\n{val}" for key, val in row.to_dict().items()
                )
                docs.append(
                    Document(
                        page_content=message,
                        id=hashlib.sha256(message.encode()).hexdigest(),
                        metadata={
                            "category": "conversation",
                            "source": dataset_name,
                        },
                    )
                )
            docs = self.text_splitter.split_documents(docs)
            return docs
        except Exception as e:
            raise Exception(f"Error loading dataset {dataset_name}: {e}")
