import json
import requests
from pydantic import HttpUrl
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, Depends
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import  Depends, HTTPException
from fastapi import FastAPI, Depends, HTTPException, status,Request,Security,Header,Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm,APIKeyHeader
# from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse
# from jose import jwt,JWTError
from globals.passwords import API_KEY,API_PASSWORD,ALGORITHM,SECRET_KEY
from globals.Const import MOODLE_URL,MOODLE_COURSE_URL,XETID_TOKEN,API_KEY_NAME,MOODLE_WS_ENDPOINT
from routes.course_user_relations.course_user_relations import course_user_router
from routes.courses.courses import courses_router
from routes.role_users.roles_users import role_user_router
from routes.users.users import user_router
from routes.competitions.competition import competition_user_router
from models.token_model import Token
# from models.api_login import api_model

# from http.cookies import SimpleCookie



limiter = Limiter(key_func=get_remote_address,default_limits=["10 per minute"])

# Instanciar la aplicación de FastAPI
app = FastAPI()


# Agregar middleware de SlowAPI para manejar rate limiting global
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Manejador de excepciones para cuando se excede el límite de solicitudes
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        content={"detail": "Rate limit exceeded. Try again later."},
        status_code=429
)
 # Middleware CORS para gestionar los orígenes permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
    


app.description = "Moodle_Ticket_API"
app.include_router(course_user_router)
app.include_router(user_router)
app.include_router(role_user_router)
app.include_router(courses_router)
app.include_router(competition_user_router)


api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False) 





async def verify_api_key(api_key: str = Security(api_key_header)): 
    if api_key != API_KEY: 
        raise HTTPException(status_code=403, detail="Could not validate credentials") 
    return api_key


# Para obtner el link proporcionado por el plugin de autenticacion simple, sera necesario acceder a este endpoint enviando como header la apikey de seguirdad 
@app.post("/login_key",summary="Devuelve una url de autorizo lista para redirigir luego al usuario")
async def login_key(email:str,token:Annotated[str,Depends(verify_api_key)],wants_url:HttpUrl):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'auth_userkey_request_login_url',
        'moodlewsrestformat': 'json',
        'user[email]': email
    }
    posteo = requests.post(MOODLE_URL+MOODLE_WS_ENDPOINT,params=params,verify=False)
    decoded_data =posteo.content.decode()
    dict_url = json.loads(decoded_data)
    url= dict_url["loginurl"]  
    redirect_url=url+"&wantsurl="+str(wants_url)
    return RedirectResponse(url=redirect_url)

# @app.get("/Redirect")
# async def redirect_to(wants_url:str,key_url:str):
#     course = requests.post(url=f"{key_url}&wantsurl={wants_url}",verify=False)
# # https://preparatoria.xutil.cu/course/view.php?id=7
#     print(course)
    
#     return RedirectResponse(url=f"{key_url}&wantsurl={wants_url}")
    # return HTMLResponse(content=course.content)
# @app.get("/login")
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
#     url_protegida = f"{MOODLE_COURSE_URL}{course_id}?token={token}"
#     return url_protegida

@app.get("/mi-ip")
async def obtener_ip_cliente(request: Request):
    ip_cliente = request.client.host
    return {"ip_cliente": ip_cliente}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
