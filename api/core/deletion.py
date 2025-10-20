from langchain_astradb import AstraDBVectorStore


class Deletion:
    def __init__(self, vectorstore: AstraDBVectorStore):
        self.vectorstore = vectorstore

    def delete_docs(
        self,
        source: str = None,
        category: str = None,
        sub_category: str = None,
    ):
        """
        Delete documents from the vectorstore based on their IDs.
        """
        try:
            metadata_filter = {
                "category": category if category else None,
                "sub_category": sub_category if sub_category else None,
                "source": source if source else None,
            }
            deletion_count = self.vectorstore.delete_by_metadata_filter(
                filter=metadata_filter,
            )
            return deletion_count
        except Exception as e:
            raise Exception(f"Error deleting documents: {e}")
