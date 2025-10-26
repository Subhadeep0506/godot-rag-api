import uuid
from api.utils.rtd_reader import ReadTheDocsReader
from api.utils.parqet_reader import ConversationsReader
from api.models.sources import Source as SourceModel
from tqdm import tqdm
from api.config.state import State


class Ingestion:
    def __init__(self):
        self.rtd_loader = ReadTheDocsReader()
        self.conversationds_loader = ConversationsReader()

    def ingest_docs(self, directory: str, db):
        try:
            State.logger.info(f"Starting ingestion from {directory}")
            docs = self.rtd_loader.load(directory=directory)
            chunk_size = 100
            total = len(docs)
            State.logger.info(f"Loaded {total} documents from {directory}")
            total_chunks = (total + chunk_size - 1) // chunk_size
            with tqdm(
                total=total_chunks,
                desc="Ingesting documents in 100 chunk sizes...",
                unit="chunk",
            ) as pbar:
                for i in range(0, total, chunk_size):
                    chunk = docs[i : i + chunk_size]
                    _ = State.vector_store.add_documents(
                        documents=chunk,
                    )
                    _ = pbar.update(1)

            categories = set()
            sub_categories = set()
            sources = set()
            tags = set()
            for doc in docs:
                metadata = doc.metadata
                if "category" in metadata:
                    categories.add(metadata["category"])
                if "sub_category" in metadata:
                    sub_categories.add(metadata["sub_category"])
                if "source" in metadata:
                    sources.add(metadata["source"])
                if "tags" in metadata and isinstance(metadata["tags"], list):
                    for tag in metadata["tags"]:
                        tags.add(tag)

            source_entry = SourceModel(
                source_id=str(uuid.uuid4()),
                title="Godot Docs",
                tags=list(tags),
                sources=list(sources),
                categories=list(categories),
                sub_categories=list(sub_categories),
                document_count=total,
            )
            db.add(source_entry)
            db.commit()
            State.logger.info(
                f"Finished ingestion from {directory}, ingested {total} documents."
            )
        except Exception as e:
            State.logger.error(f"Error during ingestion: {e}")

    def ingest_conversations(self, dataset_name: str, db):
        try:
            docs = self.conversationds_loader.load(dataset_name=dataset_name)
            total = len(docs)
            chunk_size = 100
            State.logger.info(f"Loaded conversations from {dataset_name}")

            total_chunks = (total + chunk_size - 1) // chunk_size
            with tqdm(
                total=total_chunks,
                desc="Ingesting conversations in 100 chunk sizes...",
                unit="chunk",
            ) as pbar:
                for i in range(0, total, chunk_size):
                    chunk = docs[i : i + chunk_size]
                    _ = State.vector_store.add_documents(
                        documents=chunk,
                    )
                    pbar.update(1)
                    State.logger.info(f"Ingested {i+chunk_size}/{total} chunks.")
            categories = set()
            sub_categories = set()
            sources = set()

            for doc in docs:
                metadata = doc.metadata
                if "category" in metadata:
                    categories.add(metadata["category"])
                if "sub_category" in metadata:
                    sub_categories.add(metadata["sub_category"])
                if "source" in metadata:
                    sources.add(metadata["source"])
            source_entry = SourceModel(
                source_id=str(uuid.uuid4()),
                title=dataset_name,
                tags=[],
                sources=list(sources),
                categories=list(categories),
                sub_categories=list(sub_categories),
                document_count=total,
            )
            db.add(source_entry)
            db.commit()

            State.logger.info(
                f"Finished ingestion of {dataset_name}, ingested {total} Conversations."
            )
        except Exception as e:
            State.logger.error(f"Error during ingestion: {e}")

    def ingest_from_sitemap(self, sitemap_url: str, db):
        try:
            State.logger.info(f"Starting ingestion from sitemap: {sitemap_url}")
            total = 0
            # TODO: Implement sitemap reader and ingestion logic
            State.logger.info(
                f"Finished ingestion from sitemap: {sitemap_url}, ingested {total} documents."
            )
        except Exception as e:
            State.logger.error(f"Error during ingestion from sitemap: {e}")
