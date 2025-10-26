from api.services.logger_service import LoggerService


class SingletonMeta(type):
    """A metaclass for creating singleton classes."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class State(metaclass=SingletonMeta):
    """Application global state (singleton).

    This class intentionally avoids importing or instantiating controllers at
    module import / class definition time to prevent circular imports. Use
    `initialize_controllers()` to lazily import and create controller
    instances once the application is starting up.
    """

    # default class-level attributes kept for backward compatibility
    logger = LoggerService.get_logger()
    embeddings = None
    vector_store = None

    query_controller = None
    session_controller = None
    message_controller = None
    ingestion_controller = None
    source_controller = None

    def __init__(self):
        self._logger_service = LoggerService().get_logger()
        # ensure instance logger is the logger service instance
        self.logger = self._logger_service
        self._controllers_initialized = False

    def initialize_embeddings_and_vectorstore(self):
        try:
            from api.services.embeddings_factory import EmbeddingsFactory
            from api.services.vector_store_factory import VectorStoreFactory

            emb = EmbeddingsFactory().get_embeddings(
                "sentence-transformers", "intfloat/multilingual-e5-large-instruct"
            )

            vs = VectorStoreFactory().get_vectorstore(
                vectorstore_service="astradb",
                embeddings=emb,
            )
            self.embeddings = emb
            State.embeddings = emb

            self.vector_store = vs
            State.vector_store = vs
        except Exception as e:
            self.logger.error(f"Error initializing embeddings and vectorstore: {e}")
            raise

    def initialize_controllers(self):
        """Lazily import and instantiate core controllers.

        This method is safe to call multiple times; initialization will run
        only once. Imports are done inside the method body to avoid
        import-time circular dependencies between modules that also import
        `State`.
        """
        if getattr(self, "_controllers_initialized", False):
            return

        lg = getattr(self, "logger", None)
        try:
            from api.core.query import Query
            from api.core.session import Session
            from api.core.source import Source
            from api.core.session_message import SessionMessage
            from api.core.ingestion import Ingestion

            try:
                qc = Query()
                self.logger.info("Query controller instantiated successfully.")
            except Exception as e:
                if lg:
                    lg.error(f"Failed to instantiate Query controller: {e}")
                raise

            ic = None
            try:
                ic = Ingestion()
                self.logger.info("Ingestion controller instantiated successfully.")
            except Exception as e:
                if lg:
                    lg.warning(f"Failed to create Ingestion with vectorstore: {e}")
                ic = None

            sc = None
            try:
                sc = Session()
                self.logger.info("Session controller instantiated successfully.")
            except Exception as e:
                if lg:
                    lg.error(f"Failed to instantiate Session controller: {e}")

            mm = None
            try:
                mm = SessionMessage()
                self.logger.info("SessionMessage controller instantiated successfully.")
            except Exception as e:
                if lg:
                    lg.error(f"Failed to instantiate SessionMessage controller: {e}")

            try:
                src = Source()
                self.logger.info("Source controller instantiated successfully.")
            except Exception as e:
                if lg:
                    lg.error(f"Failed to instantiate Source controller: {e}")
                src = None

            # assign controllers to both instance and class attributes so
            # existing code that references State.<controller> works.
            self.query_controller = qc
            State.query_controller = qc

            self.session_controller = sc
            State.session_controller = sc

            self.message_controller = mm
            State.message_controller = mm

            self.ingestion_controller = ic
            State.ingestion_controller = ic

            self.source_controller = src
            State.source_controller = src
            self._controllers_initialized = True
            if lg:
                lg.info("State controllers initialized")
        except Exception as e:
            if getattr(self, "logger", None):
                self.logger.error(f"Error initializing controllers: {e}")
            raise
