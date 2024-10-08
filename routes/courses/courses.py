from fastapi import APIRouter,HTTPException,Header
from fastapi.responses import JSONResponse,Response
from globals.variables import Admin_token,MOODLE_URL,MOODLE_WS_ENDPOINT,local_url,Xetid_token,MOODLE_COURSE_URL
from models.course_model import Course
from typing import List,Annotated
from controllers.validate_response import validate_response
from jose import jwt,JWTError
from routes.course_user_relations.course_user_relations import get_users_in_course
import requests
import aiohttp
import dicttoxml
# import asyncio
import json

import time
courses_router = APIRouter(prefix="/Courses",tags=["Todas las rutas que involucren CURSOS de Moodle"])

@courses_router.get("/courses")
async def read_courses(courseid:int|None = None,moodlewrestformat:Annotated[str,Header()]="json")-> Response:
    params = {
    'wstoken': Xetid_token,
    'wsfunction': 'core_course_get_courses',
    'moodlewsrestformat': moodlewrestformat,
        # ID del curso específico
    # 'options[includeoverviewfiles]': True  # Incluir archivos de resumen
    }
    
    # overviews = [{"overviewsfiles": True}]
    if courseid:
        params.update({'options[ids][0]': courseid })
        
    try:
        async with aiohttp.ClientSession() as session:
            print("sadasdasdas")
            async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params, ssl=False) as response:
                print(response)
                return await validate_response(response)
    except aiohttp.ClientConnectorError as e:
        print(f"Connection error: {e}")
        return Response(content="Connection error", status_code=500)
    except Exception as e:
        print(f"An error occurred: {e}")
        return Response(content="An error occurred", status_code=500)
    

@courses_router.get("/courses/search", response_model=List[dict])
async def search_courses(query: str,moodlewrestformat:Annotated[str,Header()]='json'):
    courses = await read_courses(moodlewrestformat="json")
    courses = json.loads(courses.body)
    print(courses)
    filtered_courses = [course for course in courses if query.lower() in course["fullname"].lower()]
    course_list =[course for course in filtered_courses]
    if moodlewrestformat == "xml":       
        import dicttoxml
        xml_data = dicttoxml.dicttoxml(course_list)   
        return Response(content=xml_data, media_type="application/xml")    
        
    else:
        return JSONResponse(content=course_list)

#  Obtener los cursos para formar un directorio
async def obtener_cursos(session: aiohttp.ClientSession, url: str, params: dict):
    params['wsfunction'] = 'core_course_get_courses'
    async with session.get(url, params=params,ssl =False) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener los cursos de Moodle")
        print(response)
        return await response.json()
#  Obtener categorias para formar un directorio
async def obtener_categorias(session: aiohttp.ClientSession, url: str, params: dict):
    params['wsfunction'] = 'core_course_get_categories'
    async with session.get(url, params=params,ssl = False) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener las categorías de Moodle")
        print(response)
        return await response.json()
#  Obtener los archivos para formar un directorio
async def obtener_archivos( courseid: int,session: aiohttp.ClientSession, url: str, params: dict):
    params['wsfunction'] = 'core_course_get_contents'
    params['courseid'] = courseid
    async with session.get(url, params=params,ssl = False) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener los archivos de Moodle")
        print(response)
        return await response.json()

@courses_router.get("/obtener_directorio",response_description="Lista de diccionarios,cada uno contiene curso,categoria y archivos",response_model=list|bytes, )
async def obtener_directorio(moodlewrestformat:Annotated[str | None, Header()] = "xml"):
    url = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        'wstoken': Xetid_token,
        'moodlewsrestformat': 'json'
    }
    async with aiohttp.ClientSession() as session:
        # Obtener categorías
        categorias = await obtener_categorias(session, url, params)
        
        # Obtener cursos
        cursos = await obtener_cursos(session, url, params)
        
        directorio = []
        for curso in cursos:
            # print(curso["id"])
            # Obtener archivos para cada curso
            archivos = await obtener_archivos(curso['id'],session, url, params )
            
            # Combinar datos en una estructura
            directorio.append({
                'curso': curso,
                'categoria': next((cat for cat in categorias if cat['id'] == curso['categoryid']), None),
                'archivos': archivos
            })
    if moodlewrestformat == "xml":       
        xml_data = dicttoxml.dicttoxml(directorio)    
        print(type(xml_data))   
        return Response(content=xml_data, media_type="application/xml")
    else:
        print(type(directorio))  
        return JSONResponse(content=directorio)
        
@courses_router.get("/course-cover/{course_id}")
async def get_course_cover(course_id: int):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': "core_course_get_courses_by_field",
        'moodlewsrestformat': 'json',
        'field': 'id',  # Buscar por el ID del curso
        'value': course_id
    }
    print(course_id)
    
    async with aiohttp.ClientSession() as session:
        
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            courses = await response.json()
            print(courses)
            # Verificamos si obtuvimos cursos
            if 'courses' in courses and isinstance(courses['courses'], list):
                course = courses['courses'][0]  # Primer curso encontrado

                # Buscamos archivos de resumen (overview files)
                course_summary_files = course.get('overviewfiles', [])
                
                # Si hay archivos de resumen, buscamos una imagen
                for file in course_summary_files:
                    if file['mimetype'].startswith('image/'):
                        # Devuelve la URL de la imagen con el token para acceder
                        return {"cover_image_url": f"{file['fileurl']}?token={Xetid_token}"}
            
            return {"message": "Imagen de portada no encontrada o curso sin imagen."}
    

# @courses_router.get("/course_url/{course_id}")
# def get_course_url(course_id: int):
#     course_url = f"{MOODLE_COURSE_URL}?id={course_id}"
#     return {"course_url": course_url}
# garbage-----:
# SECRET_KEY = "secret_key"
# MOODLE_Course_URL_id = MOODLE_COURSE_URL+"?id="
# @courses_router.get("/course_url")
# def generar_url_segura(course_id, user_id):
#     # Genera un token con la información del curso y usuario
#     payload = {
#         "course_id": course_id,
#         "user_id": user_id,
#         "exp": time.time() + 1000  # Expiración en 5 minutos
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#     print(token)
    
#     # URL protegida con el token como parámetro
#     url_protegida = f"{MOODLE_Course_URL_id}{course_id}?token={token}"
#     return url_protegida



# @courses_router.get("/acceso-curso")
# async def acceso_curso(token: str):
#     try:
#         # Verifica el token
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         user_id = payload.get("user_id")
#         course_id = payload.get("course_id")
#         print(course_id)
#         print(user_id)
#         # Verifica si el token ha expirado
#         if payload["exp"] < time.time():
#             raise HTTPException(status_code=401, detail="Token expirado")

#         # Comprueba si el usuario ya está matriculado en el curso
        
#         enrolled_users =  await get_users_in_course( course_id = course_id,user_id = user_id,moodlewrestformat="json")
#         # print(enrolled_users)
#         # print(enrolled_users.body)
#         enrolled_users_data = json.loads(enrolled_users.body.decode('utf-8'))
#         print("enrolled users data")
#         print(enrolled_users_data)
#         # bool_matriculate = False    # Verifica si el user_id está en la lista de usuarios matriculados
#         for user in enrolled_users_data:
#             print(user["id"])
#             print(user_id)
#             if int(user["id"]) == int(user_id):
#                 # bool_matriculate =True
#                 print("cheking id")
#                 return "el usuario ya esta matriculado"     
#         print("matriculando")         # Matricula al usuario automáticamente
#         await matricular_usuario(user_id, course_id)

#         # Redirige al curso en Moodle
#         url_curso = f"http://localhost:4000/course/view.php?id={course_id}"
#         return {"redirect_url": url_curso}
    
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expirado")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Token inválido")
@courses_router.get("/Obtener_archivos")
async def obtener_archivos_single(courseid: int,moodlewsrestformat:Annotated[str,Header()]="json"):
    course =  await read_courses(courseid)
    course = json.loads(course.body.decode("utf-8"))
    criteria ={}
   
    criteria['criteria[0][key]'] = 'id'
    criteria['criteria[0][value]'] =course[0]["categoryid"]

    params ={
        'wstoken': Xetid_token,
        'moodlewsrestformat': 'json',
        'wsfunction': 'core_course_get_contents',
        'courseid':  courseid  
     }
    criteria.update({"wstoken":params["wstoken"],"moodlewsrestformat":"json"})
    directorio = []
    # params['wsfunction'] = 'core_course_get_contents'
    # params['courseid'] = courseid
    async with aiohttp.ClientSession() as session:
        category = await obtener_categorias(session,MOODLE_URL +MOODLE_WS_ENDPOINT,params=criteria)
        async with session.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener los archivos de Moodle")
            print(response)
            archivos = await response.json()
        directorio.append({
                'curso': course,
                'categoria': category,
                'archivos': archivos
            })
        if moodlewsrestformat == "xml":                 
            xml_data = dicttoxml.dicttoxml(directorio)    
            print(type(xml_data))   
            return Response(content=xml_data, media_type="application/xml")
        else:
            print(type(directorio))  
            return JSONResponse(content=directorio)
            
# async def get_users_in_course(course_id:int,user_id:int,moodlewrestformat:Annotated[str,Header()]="xml"):
#     url = MOODLE_URL + MOODLE_WS_ENDPOINT
#     function = "core_enrol_get_enrolled_users"

#     params = {
#         "wstoken": Xetid_token,
#         "wsfunction": function,
#         "moodlewsrestformat": moodlewrestformat,
#         "courseid": course_id  # Reemplaza course_id con el ID del curso
#     }

#     async with aiohttp.ClientSession() as session:       
#         async with session.get(url, params=params, ssl=False) as response:   
#             print(response.status)
#             print(response.headers.get("Content-Type"))
#             if response.status!= 200:
#                 raise HTTPException(status_code=response.status, detail="Error al intentar obtener informacion del sitio")
#             enrolled_users =  await validate_response(response)
#             for user in enrolled_users:
#                 if user["id"] == user_id:
#                     print(True)
#                     return True
#             print(False)
#             return False
        
# Función para verificar si el usuario está matriculado
async def esta_matriculado(user_id, course_id):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'core_enrol_get_enrolled_users',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params) as response:
            enrolled_users = await response.json()

            # Verifica si el user_id está en la lista de usuarios matriculados
            for user in enrolled_users:
                if user["id"] == user_id:
                    return True
            return False


# Función para matricular automáticamente al usuario
async def matricular_usuario(user_id, course_id):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json',
        'enrolments[0][roleid]': 5,  # Estudiante
        'enrolments[0][userid]': user_id,
        'enrolments[0][courseid]': course_id
    }

    async with aiohttp.ClientSession() as session:
        await session.post(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params) 
           