from pydantic import BaseModel
from typing import Optional, Dict, Any


class QueryState(BaseModel):
    model_name: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    temperature: float = 0.7
    top_k: int = 10
    memory_service: str
    reddit_username: Optional[str] = None
    relevance: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    session_id: str
    state: QueryState


class QueryResponse(BaseModel):
    response: Dict[Any, Any]
