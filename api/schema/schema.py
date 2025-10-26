from pydantic import BaseModel, Field
from typing import Optional


class QuerySchema(BaseModel):
    query: str = Field(..., description="User query text", example="How do I animate a sprite in Godot?")
    category: Optional[str] = Field(None, description="Optional retrieval category", example="gameplay")
    sub_category: Optional[str] = Field(None, description="Optional retrieval sub category", example="animation")
    session_id: str = Field(..., description="Session id to attach query to", example="session-1234")
    temperature: float = Field(0.7, description="LLM temperature", example=0.7)
    model: str = Field(..., description="Model name to use", example="gpt-4o-mini")