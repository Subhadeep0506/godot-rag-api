from pydantic import BaseModel
from typing import Optional

class QuerySchema(BaseModel):
    query: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    session_id: str
    temperature: float
    model: str