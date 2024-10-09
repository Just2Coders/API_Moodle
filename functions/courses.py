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