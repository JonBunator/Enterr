from pydantic import BaseModel
from typing import Optional, Any


class ApiPostResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None


class ApiGetResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None  # Adding an optional 'data' field
    error: Optional[str] = None
