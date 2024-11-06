from fastapi import APIRouter,HTTPException,Header,Depends,Path
from fastapi.responses import JSONResponse,Response,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from globals.Const import Xetid_token,MOODLE_URL,MOODLE_WS_ENDPOINT,oauth2_scheme
from typing import Annotated
from middlewares.connection import error_handler
from middlewares.validate_response import  validate_response
from middlewares.find_userid import find_userid
from functions import courses
from models.token_model import Token
import aiohttp
import requests
import json
import dicttoxml
# import os
# import httpx

# corroutine error en get completetion

course_user_router = APIRouter(prefix="/Course_user",tags=["Rutas que involucren relaciones de USUARIOS con CURSOS "])
course_user_router.middleware_stack

@course_user_router.post("/matricular")
@error_handler
async def enrol_user_in_course(user_id:Annotated[str,Depends(find_userid)], course_id:int, role_id:int = 5):
    print(user_id)
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json',
        'enrolments[0][roleid]': 5,  # Estudiante
        'enrolments[0][userid]': user_id,
        'enrolments[0][courseid]': course_id
    }
    # try:
    async with aiohttp.ClientSession() as session:
        response = await session.post(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl=False)
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al inscribir al usuario en el curso")
        return  await response.json()
        # resp =await response.json()
        # print(resp)        
        # return JSONResponse(content=response)
    # except aiohttp.ClientConnectionError as e:
    #     raise HTTPException(status_code=502,detail="Ha fallado la conexion con el servidor Moodle")

           
    

@course_user_router.get("/get_users_in_course",summary="Este endpoint obtiene la lista de usuarios matriculados en un curso específico")
@error_handler
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
            return await validate_response(response)
@course_user_router.get("/mod_workshop_get_grades",summary="Obtiene las calificaciones de un taller (workshop).,Se necesita primero Ver los workshops para sacar el id")
@error_handler
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
        
@course_user_router.get("/mod_workshop_get_workshops",summary="Este endpoint devuelve los talleres asociados a un curso.")
@error_handler
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
@course_user_router.get("/user/completed_courses/",summary="Obtiene los cursos completados por un usuario, junto con las actividades completadas.")
@error_handler
async def get_completed_courses(user_id: Annotated[str,Depends(find_userid)]):
    print("pelfe")
    #courses_enrolled =  await 
    user_courses = await get_courses_by_user(userid=user_id)
    user_courses_serialized = json.loads(user_courses.body.decode("utf-8"))
    completed_courses = []
    response =[]
    print("cursos")
    print(user_courses_serialized)
    for course in user_courses_serialized:
        print(course["id"])
        course_completion_status = await get_course_completion_status(user_id,course["id"])
        course_completion_status_serealized = json.loads(course_completion_status.body.decode("utf-8"))    
        print("course_completion_status_serealized")   
        print(course_completion_status_serealized)
       
        if course_completion_status.status_code == 200 and course_completion_status_serealized["exception"] == "moodle_exception" :
            continue
        else:
            if course_completion_status_serealized['completionstatus']['completed']:
                completed_courses.append(
                    {"fullname":course["fullname"],
                     "id":course["id"]})
            
    for course in completed_courses:
        activities_completion_status = await get_activities_completion_status(courseid=course['id'], user_id=user_id)
        activities_completion_status_serialized = json.loads(activities_completion_status.decode("utf-8"))
        completed_activities = [activity for activity in activities_completion_status_serialized if activity['state'] == 1]
        response.append({
            'course_id': course['id'],
            'course_name': course['fullname'],
            'completed_activities': completed_activities
        })
           
    return JSONResponse(content=response)

@course_user_router.get("/course_completion_status",summary='Obtiene el estado de finalización de un curso específico para un usuario.,Tener en cuenta que hay q configurar los criterios para la terminacion del curso')
@error_handler
async def get_course_completion_status(user_id:Annotated[str,Depends(find_userid)],courseid:int,moodlewsrestformat:Annotated[str,Header()]="json"):
    
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
       
@course_user_router.get("/courses_by_user",summary="Obtiene la lista de cursos a los que un usuario está matriculado")
@error_handler
async def get_courses_by_user(userid:Annotated[str,Depends(find_userid)],moodlewsrestformat:Annotated[str,Header()]="json"):
    params ={
        "wstoken":Xetid_token,
        "wsfunction":"core_enrol_get_users_courses",
        "moodlewsrestformat":moodlewsrestformat,
        "userid":userid
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=MOODLE_URL+MOODLE_WS_ENDPOINT,params=params,ssl=False) as response :
            return await validate_response(response)
    
        
@course_user_router.get("/activities_completion_status",summary="Este endpoint devuelve el estado de finalización de las actividades de un curso específico para un usuario.")
@error_handler
async def get_activities_completion_status(course_id: int, user_id: Annotated[str,Depends(find_userid)],moodlewsrestformat:Annotated[str,Header()]="json"):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_completion_get_activities_completion_status',
        'moodlewsrestformat': moodlewsrestformat,
        'courseid': course_id,
        'userid': user_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            print(response)
            # completion_status = await response.json()
            return await validate_response(response)

@course_user_router.get("/Obtener_archivos_by_tokenuser")
async def obtener_archivos_single_by_token(courseid: int,Token:Annotated[str,Depends(oauth2_scheme)],moodlewsrestformat:Annotated[str,Header()]="json"):  
    # criteria['criteria[0][key]'] = 'id'
    # criteria['criteria[0][value]'] =course[0]["categoryid"]

    params ={
        'wstoken': Token,
        'moodlewsrestformat': 'json',
        'wsfunction': 'core_course_get_contents',
        'courseid':  courseid  
     }

    print(Token)
    directorio = []
    # params['wsfunction'] = 'core_course_get_contents'
    # params['courseid'] = courseid
    async with aiohttp.ClientSession() as session:
        criteria ={}
        criteria.update({"wstoken":Token,"moodlewsrestformat":"json"})
        course =  await courses.obtener_cursos(session,MOODLE_URL+MOODLE_WS_ENDPOINT,criteria,courseid)
        print("course")
        print(course)
        print(type(course))
        print(course[0]["categoryid"])
        print(type(course[0]["categoryid"]))
        id_cat = course[0]["categoryid"]
        print(criteria)
        category = await courses.obtener_categorias(session,MOODLE_URL+MOODLE_WS_ENDPOINT,criteria,id=id_cat)
        print(category[0]["path"])
        parents:str = category[0]["path"]
        ids= parents.replace("/",",")
        print(ids)
        # print(category)
        # parents_array = parents.split("/")
        # str_parents = ""
        # for parent in parents_array:
        #     str_parents= parent + str_parents
        categories = await courses.obtener_categorias(session,MOODLE_URL+MOODLE_WS_ENDPOINT,criteria,ids=ids)
        print("categories")
        print(categories)
        # category_tarjet = [cat for cat in category if  cat["id"] == course[0]["categoryid"]] 
        # print(category_tarjet)   

        # categories =[]
        # if category_tarjet[0]["depth"] == 1:
        #     categories.append(category_tarjet[0])
        # else:
        #     for parent in parents_array:
        #         print(parent)           
        #         if parent == "":
        #             continue   
        #         for  cat in category:
        #             if cat["id"] == int(parent):
        #                 categories.append(cat)
        #                 break
                    
                
            # categories = [cat for cat in category if cat["id"] == int(parent)]
            # print(categories) 

        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener los archivos de Moodle")
            print(response)
            archivos = await response.json()
        directorio.append({
                'curso': course,
                'categoria': categories,
                'archivos': archivos
            })
        if moodlewsrestformat == "xml":                 
            xml_data = dicttoxml.dicttoxml(directorio)    
            print(type(xml_data))   
            return Response(content=xml_data, media_type="application/xml")
        else:
            print(type(directorio))  
            return JSONResponse(content=directorio)
# @course_user_router.get("/contents")
# async def obtener_archivos( courseid: int,session: aiohttp.ClientSession, url: str, params: dict):
#     params['wsfunction'] = 'core_course_get_contents'
#     params['courseid'] = courseid
#     async with session.get(url, params=params,ssl = False) as response:
#         if response.status != 200:
#             raise HTTPException(status_code=response.status, detail="Error al obtener los archivos de Moodle")
#         print(response)
#         return await response.json()
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