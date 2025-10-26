from api.config.state import State
from api.models.sources import Source as SourceModel


class Source:
    def __init__(self):
        pass

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
            deletion_count = State.vector_store.delete_by_metadata_filter(
                filter=metadata_filter,
            )
            return deletion_count
        except Exception as e:
            State.logger.error(f"Error deleting documents: {e}")
            raise Exception(f"Error deleting documents: {e}")

    def list_sources(self, db) -> list:
        """
        List all unique sources in the vectorstore.
        """
        try:
            sources = db.query(SourceModel).all()
            return sources
        except Exception as e:
            State.logger.error(f"Error listing sources: {e}")
            raise Exception(f"Error listing sources: {e}")
