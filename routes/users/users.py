from fastapi import APIRouter,HTTPException,Header
from fastapi.responses import JSONResponse,Response,RedirectResponse
from globals.Const import Xetid_token,MOODLE_URL,MOODLE_WS_ENDPOINT,xetid_url,Admin_token,local_url
from globals.passwords import password
# from globals.passwords import password
from models.user_model import User_in,UserSearch
from typing import Annotated
from controllers.validate_response import validate_response
import aiohttp
# import requests
# import httpx
import json

# Para obtener todas las cosas completadas dado un usuario  mod_workshop_   get_grades,reviewer_assessments
# verificar q un topico este completado antes de entrar a otro topico

user_router = APIRouter(prefix="/User",tags=["Todas las rutas relacionadas con USUARIOS solamente"])


@user_router.post("/registrar_usuario")
async def registrar_usuario(user: User_in):
    url = f"{MOODLE_URL}/webservice/rest/server.php?"
    # 53 hasta 71 noooo
    firstname = lambda : user.username[:round(len(user.username) / 2)]
    print(firstname)

# Definir los parámetros de la solicitud
    params = {
    'wstoken': Xetid_token,
    'wsfunction': 'core_user_create_users',
    'moodlewsrestformat': 'json',
    'users[0][username]': user.username,
    'users[0][password]': f"{password}{user.username}",
    'users[0][firstname]': firstname(),
    'users[0][lastname]': user.username[len(firstname()): ],
    'users[0][email]': user.email
    # "users[0][roleid]": user.roleid,
    # "users[0][contextid]":user.contextid
    }

   
# Realizar la solicitud POST
    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:
    # response = requests.post(url, params=params)
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al crear el usuario en Moodle")
            data = await response.json()
            print(data)
            return(data)
@user_router.get("/site_info")
async def get_site_info(moodlewsrestformat:Annotated[str,Header()]="json"):
    params={
        "wstoken":Xetid_token,
        "wsfunction":"core_webservice_get_site_info",
        "moodlewsrestformat": moodlewsrestformat
    }
    async with aiohttp.ClientSession() as session:       
        async with session.get(xetid_url+ MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:  
            # data = await response.json()
            # print(data)
            print("type")
            print(type(response.content)) 
            text = await response.text()
            print("type")
            print("content")
            print(text)          
            print(response.headers.get("Content-Type"))    
            return await validate_response(response)
        
# async def fetch_user(criteria):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(MOODLE_URL+ MOODLE_WS_ENDPOINT, data=criteria,ssl = False) as response:
#             print(response.content)          
#             if response.status != 200:
#                 raise HTTPException(status_code=response.status, detail="Error fetching user")
#             user=  await response.json()
#             return  JSONResponse(content=user)

@user_router.post("/verify_user/")
async def verify_user(user_search: UserSearch):
    # Preparar los parámetros de búsqueda
    criteria = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_user_get_users',
        'moodlewsrestformat': 'json',
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
            print(response.content)          
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error fetching user")
            user=  await response.json()
            
        # users_data = json.loads(users.body)
        # print(users_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")   
    return user
@user_router.get("/user-progress/{user_id}",summary="Este endpoint devuelve las calificaciones de los cursos en los que un usuario está matriculado.")
async def get_user_progress(user_id: int):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'gradereport_overview_get_course_grades',
        'moodlewsrestformat': 'json',
        'userid': user_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            grades = await response.json()
            return {"user_grades": grades}

@user_router.get("/user-badges/{user_id}",summary="Este endpoint devuelve las insignias obtenidas por un usuario.")
async def get_user_badges(user_id: int):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_badges_get_user_badges',
        'moodlewsrestformat': 'json',
        'userid': user_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            badges = await response.json()
            return {"user_badges": badges}
        







# @user_router.post("/registrar_usuario")
# def registrar_usuario(user: User):
#     url = f"{MOODLE_URL}/webservice/rest/server.php?"
#     # 53 hasta 71 noooo
#     # users = [{
#     #     'username': user.username,
#     #     'password': user.password,
#     #     'firstname': user.firstname,
#     #     'lastname': user.lastname,
#     #     'email': user.email,
#     #     'auth': user.auth,
#     #     'createpassword':user.createpassword
#     # }, ]
#     # params = {
#     #     'wstoken': Xetid_token,
#     #     'wsfunction': 'core_user_create_users',
#     #     'moodlewsrestformat': 'json',
#     #     'users' : users[0]
    
#     # }
   
#     # print(users)
#     response = requests.post(f"{url}wstoken={Xetid_token}&wsfunction=core_user_create_users&moodlewsrestformat=json&users[0][username]={user.username}&users[0][password]={user.password}&users[0][firstname]={user.firstname}&users[0][email]={user.email}&users[0][lastname]={user.lastname}&users[0][auth]={user.auth}")
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error al crear el usuario en Moodle")
#     data = response.json()
#     print(data)
#     return(data)