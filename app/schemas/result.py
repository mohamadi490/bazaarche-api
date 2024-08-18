from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from schemas.pagination import Pagination

# Define a TypeVar for generic type
T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """
    A generic response model for API results.

    This class uses Pydantic's BaseModel and Python's Generic type system to create
    a flexible response structure that can accommodate various data types.

    Attributes:
        isDone (bool): Indicates whether the operation was successful.
        data (Optional[T]): The main payload of the response. Can be of any type T.
                            Defaults to None if no data is provided.
        message (Optional[str]): An optional message providing additional information
                                 about the result. Defaults to None.

    Type Parameters:
        T: The type of the data being returned.

    Example:
        result = Result[List[User]](isDone=True, data=[user1, user2], message="Users fetched successfully")
    """
    isDone: bool
    data: Optional[T] = None  # Default to None if no data is provided
    message: Optional[str] = None

class PaginationResult(Result[T]):
    """
    A generic response model for paginated results.

    This class extends the base Result model to include pagination information.
    It uses Pydantic's BaseModel and Python's Generic type system.

    Attributes:
        isDone (bool): Indicates whether the operation was successful.
        data (Optional[T]): The paginated data of type T. Defaults to None.
        pagination (Optional[Pagination]): Pagination information. Defaults to None.
        message (Optional[str]): An optional message providing additional information.

    Type Parameters:
        T: The type of the data being returned.
    """
    pagination: Optional[Pagination] = None