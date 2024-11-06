from fastapi import APIRouter,HTTPException,Header
from fastapi.responses import JSONResponse,Response
from globals.Const import MOODLE_URL,MOODLE_WS_ENDPOINT,Xetid_token
from models.course_model import Course
from typing import List,Annotated
from middlewares.validate_response import validate_response
from jose import jwt,JWTError
from functions import courses
from routes.course_user_relations.course_user_relations import get_users_in_course
from middlewares.connection import error_handler
import requests
import aiohttp
import dicttoxml
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


@courses_router.get("/obtener_directorio",response_description="Lista de diccionarios,cada uno contiene curso,categoria y archivos",response_model=list|bytes, )
async def obtener_directorio(moodlewrestformat:Annotated[str | None, Header()] = "xml"):
    url = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        'wstoken': Xetid_token,
        'moodlewsrestformat': 'json'
    }
    async with aiohttp.ClientSession() as session:
        # Obtener categorías
        categorias = await courses.obtener_categorias(session, url, params)
        
        # Obtener cursos
        cursos = await courses.obtener_cursos(session, url, params)
        
        directorio = []
        for curso in cursos:
            # print(curso["id"])
            # Obtener archivos para cada curso
            archivos = await courses.obtener_archivos(curso['id'],session, url, params )
            
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
    
@courses_router.get("/Obtener_archivos")
async def obtener_archivos_single(courseid: int,moodlewsrestformat:Annotated[str,Header()]="json"):
    course =  await read_courses(courseid)
    print(course)
    course = json.loads(course.body.decode("utf-8"))
    criteria ={}
   
    # criteria['criteria[0][key]'] = 'id'
    # criteria['criteria[0][value]'] =course[0]["categoryid"]

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
        category = await courses.obtener_categorias(session,MOODLE_URL +MOODLE_WS_ENDPOINT,params=criteria)
        category_tarjet = [cat for cat in category if  cat["id"] == course[0]["categoryid"]] 
        print(category_tarjet)   
        parents:str = category_tarjet[0]["path"]
        parents_array = parents.split("/")
        categories =[]
        if category_tarjet[0]["depth"] == 1:
            categories.append(category_tarjet[0])
        else:
            for parent in parents_array:
                print(parent)           
                if parent == "":
                    continue   
                for  cat in category:
                    if cat["id"] == int(parent):
                        categories.append(cat)
                        break
                    
                
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
@courses_router.get("/get_categories_root")
@error_handler
async def obtener_categorias_root():
    params={
    'wstoken': Xetid_token,
    'moodlewsrestformat':"json",
    }
    
    async with aiohttp.ClientSession() as session:
        categories = await courses.obtener_categorias(session,MOODLE_URL+MOODLE_WS_ENDPOINT,params)  
        response:list =[]    
        category_root = [cat for cat in categories if  cat["depth"] == 1]  
        for categ in category_root:
            first_childs_Json = await obtener_categorias_first_herarchy(categ["id"])     
            serialized_first_childs =json.loads(first_childs_Json.body.decode("utf-8")) 
            # print("serialized")
            # print(serialized_first_childs)
            json_data ={"Root": categ,"Childs":serialized_first_childs["direct_childs"] }
            response.append(json_data)
        return JSONResponse(content={"Directory":response})
        
@courses_router.get("/get_categories_first_herarchy/{parent}")
@error_handler
async def obtener_categorias_first_herarchy(parent:int):
    params={
    'wstoken': Xetid_token,
    'moodlewsrestformat':"json",
    }
    async with aiohttp.ClientSession() as session:
        categories = await courses.obtener_categorias_hijas(session,MOODLE_URL+MOODLE_WS_ENDPOINT,parent,params)
        # print("categorias hijas")
        # print(categories)
        root = await courses.obtener_categorias(session,MOODLE_URL+MOODLE_WS_ENDPOINT,params,id=parent)
        # print("categoria padre")
        # print(root)
        depth = root[0]["depth"]       
        next_level = [cat for cat in categories if cat["depth"] == depth + 1]
        # print("next_level")
        # print(next_level)
        # category_root = [cat for cat in categories if  cat["depth"] == 1]       
        # return  category_root        
        return  JSONResponse(content={"direct_childs":next_level})

@courses_router.get("/get_category_by_name")
async def obtener_categoria_by_name(name:str):
    params_child={
    'moodlewsrestformat':"json",
    'wstoken':Xetid_token,
    'wsfunction' : 'core_course_get_categories',
    'addsubcategories': 1,
    'criteria[0][key]': "name",
    'criteria[0][value]': name
    }
   
    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params_child,ssl = False) as response:

            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener las categorías de Moodle")
            return await response.json()
@courses_router.get("/get_categories_childs/{parent}")
@error_handler
async def obtener_categorias_childs(parent:int):
    params_childs={
    'wstoken': Xetid_token,
    'moodlewsrestformat':"json",
    "criteria[0][key]":"parent",
    'criteria[0][value]':parent
    }

    async with aiohttp.ClientSession() as session:
        categories = await courses.obtener_categorias_hijas(session,MOODLE_URL+MOODLE_WS_ENDPOINT,parent,params_childs)
        return categories
@courses_router.get("/category")  
async def obtener_categoria(id:int|None = None):
    params={
        "moodlewsrestformat":"json",
        "wstoken": Xetid_token
    }
    params['wsfunction'] = 'core_course_get_categories'
    params['addsubcategories']= 0
    if id:     
        params['criteria[0][key]']= "id"
        params['criteria[0][value]']= id
    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params,ssl = False) as response:
            
            respues = await response.json()
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener las categorías de Moodle")
        return respues
# Función para verificar si el usuario está matriculado
# @courses_router.get("/course_url/{course_id}")
# def get_course_url(course_id: int):
#     course_url = f"{MOODLE_COURSE_URL}?id={course_id}"
#     return {"course_url": course_url}
# garbage-----:



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