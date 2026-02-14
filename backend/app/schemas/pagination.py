from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    page: int                    # current page number (calculated)
    pages: int                   # total number of pages
    has_next: bool
    has_prev: bool


class PaginatedResponse(Generic[T], BaseModel):
    items: List[T]
    meta: PaginationMeta