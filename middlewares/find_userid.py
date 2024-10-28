from fastapi import Request, HTTPException
from models.user_model import UserSearch
from functions.user import verify_user
from middlewares.connection import error_handler

@error_handler
async def find_userid(user:UserSearch):
    # data =   await request.json()
    # email = data["username"]
    # path = request.path_params
    # query = request.query_params
    # print(path["probando"])
    # print(query)
    # print(f"{data} data")
    # user_in_request = UserSearch(**data)
    user = await verify_user(user)
    print(user)
    user_id = user["users"][0]["id"]
    print("userid")
    return user_id
    
    