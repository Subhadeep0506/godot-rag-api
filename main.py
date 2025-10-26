from dotenv import load_dotenv
import warnings

load_dotenv()
from api.core.infisical import InfisicalManagedCredentials

warnings.filterwarnings("ignore")
secrets_client = InfisicalManagedCredentials()

import os
import logfire
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api.database.database import Base, engine, DatabaseConnectionError
from api.router import query as query_router
from api.router import session as session_router
from api.router import source as source_router
from api.services.logger_service import LoggerService
from api.config.state import State

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    state = State()
    try:
        state.initialize_embeddings_and_vectorstore()
        state.initialize_controllers()
        state.logger.info("Application startup complete.")
        yield
    finally:
        qc = getattr(app.state, "query_chain", None)
        if qc is not None:
            pass
        state.logger.info("Application shutdown complete.")


tags_metadata = [
    {"name": "Health", "description": "Health and status endpoints."},
    {"name": "Query", "description": "Endpoints for processing user queries (including reddit)."},
    {"name": "Session", "description": "Session CRUD and message endpoints."},
    {"name": "Source", "description": "Manage and list external sources."},
]

app = FastAPI(
    title="RAG Chatbot API",
    description=(
        "RAG Chatbot API exposes endpoints for running retrieval-augmented generation queries, "
        "managing user chat sessions and external sources. Use the interactive docs at /docs "
        "or the OpenAPI JSON at /openapi.json to explore the API."
    ),
    version="0.1.0",
    contact={"name": "RAG API Team", "email": "devops@example.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    service_name="qwen-2.5-vl-api",
    service_version="0.0.1",
    environment=os.getenv("ENVIRONMENT", "development"),
)
logfire.instrument_fastapi(app, capture_headers=True)
logfire.instrument_sqlalchemy(engine)
logfire.instrument_httpx()
logfire.instrument_requests()
logfire.instrument_system_metrics(base="full")


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "RAG Chatbot API is running."}


@app.get("/health")
async def health_check():
    return LoggerService.log_system_info(LoggerService())


app.include_router(session_router.router, prefix="/api/v1/session")
app.include_router(query_router.router, prefix="/api/v1/query")
app.include_router(source_router.router, prefix="/api/v1/source")


@app.exception_handler(DatabaseConnectionError)
async def db_connection_exception_handler(request, exc: DatabaseConnectionError):
    State.logger.error("Database connection error: %s", exc)

    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database connection error. Please try again later.",
            "error": str(exc),
        },
    )
