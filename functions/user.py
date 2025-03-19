from fastapi import APIRouter,HTTPException,Header,Depends,Query
from fastapi.responses import JSONResponse,Response,RedirectResponse
from typing import Annotated
from globals.Const import XETID_TOKEN,MOODLE_URL,MOODLE_WS_ENDPOINT
from globals.passwords import PASSWORD
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
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_user_get_users',
        'moodlewsrestformat': "json",
    }
    if user_search.username:
        criteria['criteria[0][key]'] = 'username'
        criteria['criteria[0][value]'] = user_search.username
    # if user_search.email:
    #     criteria['criteria[1][key]'] = 'email'
    #     criteria['criteria[1][value]'] = user_search.email
    # Realizar la solicitud a la API de Moodle
    print(user_search.username)
    # users = await fetch_user(criteria)
    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+ MOODLE_WS_ENDPOINT, params=criteria,ssl = False) as response:  
            awaitye = await response.text()
            print(awaitye)
            response_data = await response.json()
            print(response)    
            # response_serialized = json.loads(response_validated.body.decode("utf-8"))
            if response_data["users"] == []:
                raise HTTPException(status_code=404,detail="Resource not found")
            else:
                return  response_data
