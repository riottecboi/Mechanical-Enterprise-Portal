from pydantic import BaseModel, Field
from typing import Union
from uuid import UUID

class NotFound(BaseModel):
    reason: str

class UserAuth(BaseModel):
    username: Union[int, str] = Field(..., description="Employee ID")
    password: str = Field(..., min_length=5, max_length=24, description="Employee password")

class UserOut(BaseModel):
    apikey: Union[UUID, None]
    username: Union[str, None]
    message: Union[str, None]
