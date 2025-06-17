# app/schemas/base_schemas.py
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar, List # Added List for PaginatedResponse example

DataType = TypeVar('DataType')

class BaseRequest(BaseModel):
    pass

class BaseResponse(BaseModel, Generic[DataType]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[DataType] = None

# Example of a paginated response, can be added later if needed.
# class PaginatedResponse(BaseResponse[DataType], Generic[DataType]):
#     page: int
#     page_size: int
#     total_items: int
#     items: List[DataType]
