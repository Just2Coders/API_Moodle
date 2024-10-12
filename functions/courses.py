import aiohttp
from fastapi import HTTPException

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