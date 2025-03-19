from fastapi import Request, HTTPException,Depends,Path
from models.user_model import UserSearch
from typing import Annotated
from functions.user import verify_user
from middlewares.connection import error_handler

@error_handler
async def find_userid(username:str):  
    user_schema = UserSearch(username=username)
    user = await verify_user(user_schema)
    user_id = user["users"][0]["id"]
    return user_id
    
    