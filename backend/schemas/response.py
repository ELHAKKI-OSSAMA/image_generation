from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
