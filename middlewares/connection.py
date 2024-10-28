from fastapi import HTTPException
import aiohttp
from functools import wraps

def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientConnectorError:
            raise HTTPException(status_code=502, detail="Error al conectar con el servidor de Moodle")
        except HTTPException as http:
             raise HTTPException(status_code=http.status_code, detail=http.detail)
        except Exception as e:                        
                raise HTTPException(status_code=500 ,detail=f"Error inesperado {e}" )
    return wrapper

