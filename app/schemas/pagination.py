from typing import Optional
from fastapi import Query
from pydantic import BaseModel


class paginationConfig(BaseModel):
    page: int = Query(1, ge=1)
    size: Optional[int] = Query(10, ge=1)

class Pagination(BaseModel):
    page: int
    size: int
    total_pages: int
    total_items: int
    
    
    @staticmethod
    def paginate_query(query, page: int, size: int):
        offset = (page - 1) * size
        paginated_query = query.offset(offset).limit(size)
        total_items = query.count()
        total_pages = (total_items + size - 1) // size
        return paginated_query, total_items, total_pages




    