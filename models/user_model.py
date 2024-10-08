from pydantic import BaseModel
class User(BaseModel):
    username:str
    password:str
    firstname: str
    lastname: str
    email: str
    auth:str
    createpassword: int
    roleid:int|None = None
    contextid:int = 1
    
class User_in(BaseModel):
    username:str
    email: str
    # roleid:int|None = None
    # contextid:int = 1

class UserSearch(BaseModel):
    username: str = None
    email: str = None