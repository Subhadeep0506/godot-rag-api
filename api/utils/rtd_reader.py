from langchain.document_loaders.readthedocs import ReadTheDocsLoader
from langchain.text_splitter import CharacterTextSplitter
from api.services.logger_service import LoggerService

logger = LoggerService.get_logger(__name__)


class ReadTheDocsReader:
    def __init__(self):
        self.loader = None
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
        )
        logger.info("ReadTheDocsReader initialized.")

    def __load_directory(self, directory: str):
        self.loader = ReadTheDocsLoader(
            path=directory,
            exclude_links_ratio=0.5,
        )
        docs = self.loader.load()
        docs = self.__apply_metadata(docs)
        docs = self.text_splitter.split_documents(docs)
        return docs

    def __apply_metadata(self, docs):
        categories = ["about", "classes", "community", "engine_details", "getting_started", "tutorials"]
        for doc in docs:
            category, sub_category = self.__extract_categories(doc.metadata["source"])
            if category in categories:
                doc.metadata["category"] = category
            if sub_category:
                doc.metadata["sub_category"] = sub_category
            # metadata = doc.metadata
            # cat = metadata["source"].split("latest/")[-1].split("/")[0]
            # if cat in categories:
            #     doc.metadata["category"] = cat
        return docs

    def __extract_categories(self, path):
        parts = path.split("latest/")
        if len(parts) != 2:
            return None, None
        path_after_latest = parts[1].strip("/")

        components = path_after_latest.split("/")
        category = components[0] if len(components) > 0 else None
        subcategory = None
        if len(components) > 1:
            if not components[1].endswith(".html"):
                subcategory = components[1]

        return category, subcategory

    def load(self, directory: str):
        """
        Load the ReadTheDocs documentation from the specified directory.
        """
        docs = self.__load_directory(directory)
        return docs
