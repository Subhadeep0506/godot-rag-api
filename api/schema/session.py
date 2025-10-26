from typing import Optional

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user creating the session", example="user_abc")
    title: Optional[str] = Field(None, description="Optional title for the session", example="Godot debugging")


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(None, description="New title for the session", example="Renamed session")
