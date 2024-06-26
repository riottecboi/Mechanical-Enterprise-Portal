from pydantic import BaseModel, Field
from typing import Union, List, Dict
from uuid import UUID

class RetResponse(BaseModel):
    msg: str

class UserAuth(BaseModel):
    username: Union[int, str] = Field(..., description="Employee ID")
    password: str = Field(..., min_length=5, description="Employee password")

class UserInfo(BaseModel):
    tt: Union[int, None]
    msnv: Union[str, None]
    fullname: Union[str, None]
    department: Union[str, None]
    gender: Union[str, None]
    vehicle: Union[str, None]
    position: Union[str, None]
    dob: Union[str, None]
    sector: Union[str, None]
    tel: Union[str, None]
    id_card: Union[int, None]
    ethnic: Union[str, None]
    nationality: Union[str, None]
    address: Union[str, None]
    ward: Union[str, None]
    district: Union[str, None]
    city: Union[str, None]
    target_group: Union[str, None]

class UserAdd(UserInfo):
    username: Union[str, None]
    password: str = Field(..., min_length=5, description="Employee password")
    confirm_password: str = Field(..., min_length=5, description="Employee confirm password")

class AdminAdd(BaseModel):
    username: Union[str, None]
    password: str = Field(..., min_length=5, description="Employee password")
    confirm_password: str = Field(..., min_length=5, description="Employee confirm password")

class UserUpdateAuth(UserInfo):
    username: Union[int, str]
    currentpw: str
    password: str
    confirm_password: str

class UserVerification(BaseModel):
    apikey: Union[UUID, None]
    username: Union[Union[int, str], None]
    is_admin: Union[bool, None]
    is_edit: Union[bool, None]
    is_view: Union[bool, None]
    message: Union[str, None]


class UserOut(UserVerification):
    tmpPWD: Union[str, None]

class UserUpdate(BaseModel):
    msnv: Union[str, None]

class UserCreated(BaseModel):
    list_pwd: Union[List[UserOut], None] = []

class UserTable(BaseModel):
    table_name: str
    status: bool