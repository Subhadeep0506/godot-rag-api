from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class QueryState(BaseModel):
    model_name: str = Field(..., description="LLM model name to use for the query", example="gpt-4o-mini")
    category: Optional[str] = Field(None, description="Optional high level category for retrieval", example="docs")
    sub_category: Optional[str] = Field(None, description="Optional sub-category", example="tutorials")
    temperature: float = Field(0.7, description="Sampling temperature for the LLM", example=0.7)
    top_k: int = Field(10, description="Number of top documents to retrieve", example=10)
    memory_service: str = Field(..., description="Memory backend identifier to use", example="default")
    reddit_username: Optional[str] = Field(None, description="Optional reddit username when using reddit retrieval", example="spez")
    relevance: Optional[str] = Field(None, description="Relevance filter for reddit queries", example="top")


class QueryRequest(BaseModel):
    query: str = Field(..., description="User input query text", example="How do I create a Node in Godot?")
    session_id: str = Field(..., description="Chat session id to associate the query with", example="session-1234")
    state: QueryState = Field(..., description="Runtime options for the query")


class QueryResponse(BaseModel):
    response: Dict[str, Any] = Field(..., description="Structured response from the query controller")

