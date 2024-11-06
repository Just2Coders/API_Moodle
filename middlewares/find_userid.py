from fastapi import Request, HTTPException,Depends,Path
from models.user_model import UserSearch
from typing import Annotated
from functions.user import verify_user
from middlewares.connection import error_handler

@error_handler
async def find_userid(username:str):
    
    # data =   await request.json()
    # email = data["username"]
    # path = request.path_params
    # query = request.query_params
    # print(path["probando"])
    # print(query)
    # print(f"{data} data")
    # user_in_request = UserSearch(**data)
    print(username)
    user_schema = UserSearch(username=username)
    user = await verify_user(user_schema)
    print(user)
    user_id = user["users"][0]["id"]
    print("userid")
    print(user_id)
    return user_id
    
    