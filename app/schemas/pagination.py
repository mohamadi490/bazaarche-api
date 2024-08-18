from pydantic import BaseModel


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




    