from pydantic import BaseModel, Field
from typing import Union, List, Dict
from uuid import UUID

class NotFound(BaseModel):
    reason: str

class UserAuth(BaseModel):
    username: Union[int, str] = Field(..., description="Employee ID")
    password: str = Field(..., min_length=5, max_length=24, description="Employee password")

class UserOut(BaseModel):
    apikey: Union[UUID, None]
    username: Union[int, None]
    is_admin: Union[bool, None]
    is_edit: Union[bool, None]
    is_view: Union[bool, None]
    message: Union[str, None]
    tmpPWD: Union[str, None]


class UserCreated(BaseModel):
    list_pwd: Union[List[UserOut], None] = []

class UserTable(BaseModel):
    table_name: str
    status: bool