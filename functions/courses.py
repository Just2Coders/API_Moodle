import aiohttp
from fastapi import HTTPException
import json
async def obtener_cursos(session: aiohttp.ClientSession, url: str, params: dict,course_id:int|None=None):
    data={
        'wsfunction':'core_course_get_courses'
    }
    data.update(params)

    if course_id:
        data['options[ids][0]']= course_id 
    async with session.get(url, params=data,ssl =False) as response:
        # course_serialized
        # if response.status == 200 and response["excpection"]:
        #     raise HTTPException(status_code=response.status, detail=response)
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener los cursos de Moodle")
        print(response.content)
        return await response.json()
#  Obtener categorias para formar un directorio
async def obtener_categorias(session: aiohttp.ClientSession, url: str, params: dict,id:int|None = None,ids:str|None=None):
    print(type(id))
    data ={
        'wsfunction':'core_course_get_categories',
        'addsubcategories': 0
    }
    data.update(params)
    # params['wsfunction'] = 'core_course_get_categories'
    # params['addsubcategories']= 0
    if id:     
        print("poniniendo ids")
        data['criteria[0][key]']= "id"
        data['criteria[0][value]']= id
    if ids:
        data['criteria[0][key]']= "ids"
        data['criteria[0][value]']= ids
    print(data)
    async with session.get(url, params=data,ssl = False) as response:
        print(response)
        respues = await response.json()
        print(respues)
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener las categorías de Moodle")
        return respues
async def obtener_categorias_hijas(session:aiohttp.ClientSession,url:str,parent:int,params:dict):
    params_child={
    'wsfunction' : 'core_course_get_categories',
    # 'addsubcategories': 1,
    'criteria[0][key]': "parent",
    'criteria[0][value]': parent
    }
    params.update(params_child)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,ssl = False) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Error al obtener las categorías de Moodle")
            return await response.json()

# async def obtener_directorio_categorias(session: aiohttp.ClientSession, url: str, params: dict):
#     print(params)
#     categoryid = params["criteria[0][value]"]
#     print(categoryid)
#     categorias = []
#     while categoryid != 0:  # Itera hasta que llegues a la categoría raíz
#         categoria = await obtener_categorias(session,url,params)
#         print(categoria)
#         if categoria:
#             categorias.insert(0, categoria[0])  # Inserta la categoría al inicio de la lista
#             categoryid = categoria[0]['parent'] # Obtén la categoría padre
#             params["criteria[0][value]"] = categoryid 
#             print("este es el params")
#             print(params["criteria[0][value]"])#actualiza en params de ibtener categortias con la categoriua padre
#             print(categoryid)
#         else:
#             break
#     return categorias
#  Obtener los archivos para formar un directorio
async def obtener_archivos( courseid: int,session: aiohttp.ClientSession, url: str, params: dict):
    params['wsfunction'] = 'core_course_get_contents'
    params['courseid'] = courseid
    async with session.get(url, params=params,ssl = False) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Error al obtener los archivos de Moodle")
        print(response)
        return await response.json()