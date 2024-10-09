from fastapi import APIRouter,HTTPException,Header
from fastapi.responses import JSONResponse,Response,HTMLResponse
from globals.Const import Xetid_token,MOODLE_URL,MOODLE_WS_ENDPOINT,local_url
from typing import Annotated
from controllers.validate_response import  validate_response
from routes.users.users import get_completion_status
import aiohttp
import requests
# import os
# import httpx
# desglozar los parents de las categorias
# corroutine error en get completetion

course_user_router = APIRouter(prefix="/Course_user",tags=["Rutas que involucren relaciones de USUARIOS con CURSOS "])

@course_user_router.post("/matricular")
async def enrol_user_in_course(user_id:str, course_id:int, role_id:int = 5):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json',
        'enrolments[0][roleid]': 5,  # Estudiante
        'enrolments[0][userid]': user_id,
        'enrolments[0][courseid]': course_id
    }

    async with aiohttp.ClientSession() as session:
        response = await session.post(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl=False)
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al inscribir al usuario en el curso")
        
        return JSONResponse(content={"message":"Matriculado con exito"})

           
    

@course_user_router.get("/get_users_in_course")
async def get_users_in_course(course_id:int,moodlewrestformat:Annotated[str,Header()]="json"):
    url =  MOODLE_URL + MOODLE_WS_ENDPOINT
    function = "core_enrol_get_enrolled_users"

    params = {
        "wstoken": Xetid_token,
        "wsfunction": function,
        "moodlewsrestformat": moodlewrestformat,
        "courseid": course_id
       
    }

    async with aiohttp.ClientSession() as session:       
        async with session.get(url, params=params, ssl=False) as response:   
            print(response.status)
            print(response.headers.get("Content-Type"))
            if response.status!= 200:
                raise HTTPException(status_code=response.status, detail="Error al intentar obtener informacion del sitio")
            return await validate_response(response)
@course_user_router.get("/mod_workshop_get_grades",summary="Se necesita primero Ver los workshops para sacar el id")
async def get_grades(workshop_id: int,moodlewsrestformat:Annotated[str,Header()]="json")->Response:
    async with aiohttp.ClientSession() as session:
        params = {
            "wstoken": Xetid_token,
            "wsfunction": "mod_workshop_get_grades",
            "moodlewsrestformat": moodlewsrestformat,
            "workshopid": workshop_id
        }
        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params,ssl=False) as response:
            print(response)
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener las calificaciones")
            return await validate_response(response)
        
@course_user_router.get("/mod_workshop_get_workshops")
async def get_workshops(course_id: int,moodlewsrestformat:Annotated[str,Header()]="json"):
    async with aiohttp.ClientSession() as session:
        params = {
            "wstoken": Xetid_token,
            "wsfunction": "mod_workshop_get_workshops_by_courses",
            "moodlewsrestformat": moodlewsrestformat,
            "courseids[0]": course_id
        }
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl=False) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener los talleres")
            # if "errorcode" in data:
            #     raise HTTPException(status_code=400, detail=data["message"])
            return await validate_response(response)
        
# async def get_activities_completion_status(course_id, user_id):
#     params = {
#         'wstoken': Xetid_token,
#         'wsfunction': 'core_completion_get_activities_completion_status',
#         'moodlewsrestformat': 'json',
#         'courseid': course_id,
#         'userid': user_id
#     }
#     async with aiohttp.ClientSession() as session:
#         async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
#             return response.json()
@course_user_router.get("/user/{user_id}/completed_courses",summary="no sirve arreglar q el get course completion status sea todos los cursos dado un userid")
async def get_completed_courses(user_id: int,courseid):
    #courses_enrolled =  await 
    course_completion_status = await get_course_completion_status(user_id,courseid)
    completed_courses = []
    print(completed_courses)
    for course in course_completion_status['statuses']:
        if course['completionstatus']['completed']:
            print(course)
            print(course['course']['id'])
            activities_completion_status = await get_completion_status(courseid=course['course']['id'], user_id=user_id)
            completed_activities = [activity for activity in activities_completion_status['statuses'] if activity['state'] == 1]
            completed_courses.append({
                'course_id': course['course']['id'],
                'course_name': course['course']['fullname'],
                'completed_activities': completed_activities
            })
    return JSONResponse(content=completed_courses)

@course_user_router.get("/course_completetion_status",summary='Tener en cuenta que hayh q configurar los criterios para laterminacion del curso')
async def get_course_completion_status(user_id:int,courseid:int,moodlewsrestformat:Annotated[str,Header()]):
    
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_completion_get_course_completion_status',
        'moodlewsrestformat': moodlewsrestformat,
        'userid': user_id,
        "courseid":courseid
    }
    async with aiohttp.ClientSession() as session:
       async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
        print("get_course")
        print(response)
        return  await validate_response(response)
@course_user_router.get("/courses_by_user/{userid}",summary="Probar q funcione")
async def get_courses_by_user(userid:int,moodlewsrestformat:Annotated[str,Header()]):
    params ={
        "wstoken":Xetid_token,
        "wsfunction":"core_enrol_get_users_courses",
        "moodlewsrestformat":moodlewsrestformat,
        "userid":userid
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=MOODLE_URL+MOODLE_WS_ENDPOINT,params=params,ssl=False) as response :
            return await validate_response(response)
# @course_user_router.get("/user/{user_id}/completed_courses")
# async def get_completed_courses(user_id: int):
#     course_completion_status = await get_course_completion_status(user_id)
#     completed_courses = []
#     print(completed_courses)

#     for course in course_completion_status['statuses']:
#         if course['completionstatus']['completed']:
#             activities_completion_status = await get_activities_completion_status(course['course']['id'], user_id)
#             completed_activities = [activity for activity in activities_completion_status['statuses'] if activity['state'] == 1]
#             completed_courses.append({
#                 'course_id': course['course']['id'],
#                 'course_name': course['course']['fullname'],
#                 'completed_activities': completed_activities
#             })

#     return JSONResponse(content=completed_courses)
    # response = requests.post(url, data=params)
    # enrolled_users = response.json()
    # print(enrolled_users)
    # return enrolled_users