from fastapi import APIRouter,HTTPException,Header,Depends,Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse,Response,RedirectResponse
from globals.Const import XETID_TOKEN,MOODLE_URL,MOODLE_WS_ENDPOINT,MOODLE_LOGIN_ENDPOINT,MOODLE_SERVICE
from globals.passwords import PASSWORD
# from globals.passwords import password
from models.token_model import Token
from models.user_model import User_in,UserSearch
from typing import Annotated
from functions.user import verify_user
from middlewares.validate_response import validate_response
from middlewares.connection import error_handler
from middlewares.find_userid import find_userid
import aiohttp
import requests
# import httpx
import json

# Para obtener todas las cosas completadas dado un usuario  mod_workshop_   get_grades,reviewer_assessments
# verificar q un topico este completado antes de entrar a otro topico

user_router = APIRouter(prefix="/User",tags=["Todas las rutas relacionadas con USUARIOS solamente"])


@user_router.post("/registrar_usuario")
@error_handler
async def registrar_usuario(user: User_in):
    url = f"{MOODLE_URL}/webservice/rest/server.php?"
    # 53 hasta 71 noooo
    firstname = lambda : user.username[:round(len(user.username) / 2)]
    lastname = user.username[len(firstname()): ]
    print(firstname)

# Definir los parámetros de la solicitud
    params = {
    'wstoken': XETID_TOKEN,
    'wsfunction': 'core_user_create_users',
    'moodlewsrestformat': 'json',
    'users[0][username]': user.username,
    'users[0][password]': f"{PASSWORD}{user.username}",
    'users[0][firstname]': firstname(),
    'users[0][lastname]': lastname,
    'users[0][email]': user.email
    # "users[0][roleid]": user.roleid,
    # "users[0][contextid]":user.contextid
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:
            print(response.status)
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al crear el usuario en Moodle")
            data = await response.json()

  
@user_router.get("/site_info")
@error_handler
async def get_site_info(moodlewsrestformat:Annotated[str,Header()]="json"):
    params={
        "wstoken":XETID_TOKEN,
        "wsfunction":"core_webservice_get_site_info",
        "moodlewsrestformat": moodlewsrestformat
    }
    async with aiohttp.ClientSession() as session:       
        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:  
            print(response.headers.get("Content-Type"))    
            return await validate_response(response)
        
@user_router.get("/get_user_course_profiles")
@error_handler
async def get_site_info(moodlewsrestformat:Annotated[str,Header()]="json"):
    params={
        "wstoken":XETID_TOKEN,
        "wsfunction":"core_user_get_course_user_profiles",
        "moodlewsrestformat": moodlewsrestformat
    }
    async with aiohttp.ClientSession() as session:       
        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:  
            # data = await response.json()
            # print(data)
            # print("type")
            # print(type(response.content)) 
            # text = await response.text()
            # print("type")
            # print("content")
            # print(text)          
            print(response.headers.get("Content-Type"))    
            return await validate_response(response)

@user_router.post("/token")
@error_handler
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # print(form_data)
    # if form_data == None:
    # #     token_data = None
    # else:
    payload = {
        'username': form_data.username,
        'password': form_data.password,
        'service': MOODLE_SERVICE
    }
    response = requests.post(MOODLE_URL + MOODLE_LOGIN_ENDPOINT, data=payload)
    print(response.content)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token_data = response.json()
    print(token_data)
    if 'token' not in token_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return Token(access_token=token_data["token"], token_type="bearer")              
        
# async def fetch_user(criteria):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(MOODLE_URL+ MOODLE_WS_ENDPOINT, data=criteria,ssl = False) as response:
#             print(response.content)          
#             if response.status != 200:
#                 raise HTTPException(status_code=response.status, detail="Error fetching user")
#             user=  await response.json()
#             return  JSONResponse(content=user)

@user_router.post("/verify_user")
@error_handler
async def verify_user_router(user_search: UserSearch):
    return  await verify_user(user_search)

@user_router.get("/user-progress",summary="Este endpoint devuelve las calificaciones de los cursos en los que un usuario está matriculado.")
@error_handler
async def get_user_progress(user_id: Annotated[str,Depends(find_userid)]):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'gradereport_overview_get_course_grades',
        'moodlewsrestformat': 'json',
        'userid': user_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            grades = await response.json()
            return {"user_grades": grades}

@user_router.get("/user-badges",summary="Este endpoint devuelve las insignias obtenidas por un usuario.")
@error_handler
async def get_user_badges(user_id: Annotated[str,Depends(find_userid)]):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_badges_get_user_badges',
        'moodlewsrestformat': 'json',
        'userid': user_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            badges = await response.json()
            return {"user_badges": badges}
        

