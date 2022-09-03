from pydantic import BaseModel, Field
from typing import Union, Any
from uuid import UUID

class TokenSubject(BaseModel):
    subject: Union[str, Any]

class TokenSchema(BaseModel):
    access_token: str

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class UserAuth(BaseModel):
    msnv: int = Field(..., description="Employee ID")
    password: str = Field(..., min_length=5, max_length=24, description="Employee password")

class UserOut(BaseModel):
    id: UUID
    msnv: str

class SystemUser(UserOut):
    password: str