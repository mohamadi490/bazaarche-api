from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# Define a TypeVar for generic type
T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """
    Create a generic response model using Pydantic's BaseModel and Python's Generic
    this class get the generic type T to return the data from the function
    """
    isDone: bool
    data: Optional[T] = None  # Default to None if no data is provided
    message: Optional[str] = None