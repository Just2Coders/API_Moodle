from pydantic import BaseModel, EmailStr
import re

class User(BaseModel):
    username: str
    password: str
    firstname: str
    lastname: str
    email: EmailStr
    auth: str
    createpassword: int
    roleid: int | None = None
    contextid: int = 1

    # @validator('password')
    # def validate_password(cls, v):
    #     if (len(v) < 8 or
    #             not re.search(r"[A-Z]", v) or
    #             not re.search(r"[a-z]", v) or
    #             not re.search(r"[0-9]", v) or
    #             not re.search(r"[\W_]", v)):
    #         raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
    #     return v

class User_in(BaseModel):
    username: str
    email: EmailStr
    # roleid:int|None = None
    # contextid:int = 1

class UserSearch(BaseModel):
    username: str = None
    email: EmailStr = None