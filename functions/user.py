from fastapi import APIRouter,HTTPException,Header,Depends,Query
from fastapi.responses import JSONResponse,Response,RedirectResponse
from globals.Const import Xetid_token,MOODLE_URL,MOODLE_WS_ENDPOINT,xetid_url,Admin_token,local_url
from globals.passwords import password
# from globals.passwords import password
from models.user_model import User_in,UserSearch
from middlewares.connection import error_handler
import aiohttp
# import requests
# import httpx
import json
@error_handler
async def verify_user(user_search: UserSearch):
    # Preparar los parámetros de búsqueda
    criteria = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_user_get_users',
        'moodlewsrestformat': "json",
    }
    if user_search.username:
        criteria['criteria[0][key]'] = 'username'
        criteria['criteria[0][value]'] = user_search.username
    if user_search.email:
        criteria['criteria[1][key]'] = 'email'
        criteria['criteria[1][value]'] = user_search.email
    # s
    # Realizar la solicitud a la API de Moodle

    # users = await fetch_user(criteria)
    async with aiohttp.ClientSession() as session:
        async with session.post(MOODLE_URL+ MOODLE_WS_ENDPOINT, data=criteria,ssl = False) as response:  
               
            response_data = await response.json()
            print(response)    
            # response_serialized = json.loads(response_validated.body.decode("utf-8"))
            if response_data["users"] == []:
                raise HTTPException(status_code=404,detail="Resource not found")
            else:
                return  response_data