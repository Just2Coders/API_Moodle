from fastapi import FastAPI, Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import JSONResponse
from jose import jwt,JWTError
from globals.Const import MOODLE_COURSE_URL,SECRET_KEY
from routes.course_user_relations.course_user_relations import course_user_router
from routes.courses.courses import courses_router
from routes.role_users.roles_users import role_user_router
from routes.users.users import user_router
from routes.competitions.competition import competition_user_router
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, Response, Depends
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from http.cookies import SimpleCookie
import requests
import json
import time
import aiohttp

limiter = Limiter(key_func=get_remote_address,default_limits=["10 per minute"])

# Instanciar la aplicación de FastAPI
app = FastAPI()

# Middleware CORS para gestionar los orígenes permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cesarfrontend"],  # Solo permitir orígenes de confianza
    allow_credentials=True,
    allow_methods=["*"],  # Métodos permitidos
    allow_headers=["*"],
)

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


app.description = "Moodle_Ticket_API"
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.include_router(course_user_router)
app.include_router(user_router)
app.include_router(role_user_router)
app.include_router(courses_router)
app.include_router(competition_user_router)



# app = FastAPI()


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





# MOODLE_URL = "https://preparatoria.xutil.cu"  # Cambia esto por tu URL de Moodle
# LOGIN_URL = f"{MOODLE_URL}/login/index.php"

# # Datos de usuario para login (ajusta con los datos correctos)
# MOODLE_USERNAME = "probandocampos"
# MOODLE_PASSWORD = "aS61idm2914ZcmAosd9ejh138*probandocampos"

# @app.post("/login")
# async def moodle_login():
#     async with aiohttp.ClientSession() as session:
#         # Primero, hacemos una solicitud GET a la página de login para obtener la cookie de sesión inicial
#         async with session.get(LOGIN_URL) as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=response.status, detail="Error al obtener la página de login")
            
#             # Extraer cookies de la sesión
#             cookies = response.cookies

#         # Ahora, enviamos las credenciales al formulario de login
#         login_data = {
#             "username": MOODLE_USERNAME,
#             "password": MOODLE_PASSWORD
#         }

#         async with session.post(LOGIN_URL, params=login_data, cookies=cookies,ssl =False) as login_response:
#             if login_response.status != 200:
#                 raise HTTPException(status_code=login_response.status, detail="Error al intentar autenticar")
#             print(cookies)
#             print(await login_response.content.read())
#             print(login_response.url)
#             # Verificamos si el login fue exitoso
#             # if 'login/index.php' in str(login_response.url):
#             #     return {"detail": "Error de autenticación. Verifica las credenciales."}
            
#             # Si login fue exitoso, ahora tenemos acceso a la sesión
#             return {"detail": "Login exitoso", "cookies": session.cookie_jar.filter_cookies(MOODLE_URL)}

# # Ejemplo de acceso a una página autenticada
# @app.get("/authenticated_page")
# async def access_authenticated_page():
#     async with aiohttp.ClientSession() as session:
#         # Primero nos autenticamos
#         login_response = await moodle_login()

#         if "Error" in login_response["detail"]:
#             raise HTTPException(status_code=401, detail="Error de autenticación")

#         # Usamos las cookies de la sesión iniciada para acceder a una página autenticada
#         async with session.get(f"{MOODLE_URL}/my/", cookies=login_response["cookies"]) as auth_response:
#             if auth_response.status != 200:
#                 raise HTTPException(status_code=auth_response.status, detail="Error al acceder a la página autenticada")
            
#             # Retornamos el contenido de la página autenticada
#             page_content = await auth_response.text()
#             return {"page_content": page_content}

# @app.post("/logueando")
# async def login(username,password):
#     MOODLE_LOGIN_ENDPOINT = "https://preparatoria.xutil.cu/login/index.php"
    
#     payload = {
#         'username': username,
#         'password': password
        
#     }
#     response = requests.post(MOODLE_LOGIN_ENDPOINT, params=payload,verify =False)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     print(response.content)
#     print("cookies\n")
#     print(response.cookies.items())
#     print(response.headers)
#     print(response.cookies.get("MoodleSession"))
#     moodle_session = response.cookies.get("MoodleSession")
#     cookie = SimpleCookie()
#     cookie["MoodleSession"] = moodle_session
#     response.cookies.set_cookie(key= "MoodleSession",value=moodle_session)


#     # cookie_header = cookie.output(header='', sep='').strip()
    
#     return {"message": "Logged in", "Set-Cookie": "joya"}

# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     MOODLE_LOGIN_ENDPOINT = "/login/token.php"
#     MOODLE_SERVICE = "miAPI"
#     payload = {
#         'username': form_data.username,
#         'password': form_data.password,
#         'service': MOODLE_SERVICE
#     }
#     response = requests.post(MOODLE_URL + MOODLE_LOGIN_ENDPOINT, data=payload)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     token_data = response.json()
#     print(token_data)
#     if 'token' not in token_data:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     return Token(access_token=token_data["token"], token_type="bearer")

# @app.get("/users/me")
# async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):

#     return {"token": token}
# @app.post("/webhook")
# async def recibir_notificacion_moodle(request: Request):
#     # Recibir los datos en formato JSON
#     try:
#         body = await request.json()

#         # Extraer la información del JSON
#         event_type = body.get('event_type')
#         user_id = body.get('userid')
#         course_id = body.get('courseid')
#         activity_id = body.get('activityid')  # Opcional, solo si es un evento de actividad

#         # Hacer algo con los datos recibidos, por ejemplo, registrarlos o procesarlos
#         print(f"Evento recibido: {event_type}")
#         print(f"Usuario ID: {user_id}, Curso ID: {course_id}, Actividad ID: {activity_id}")

#         # Puedes devolver una respuesta indicando que todo salió bien
#         return {"status": "success", "message": "Notificación recibida correctamente"}
    
#     except json.JSONDecodeError:
#         return {"status": "error", "message": "Error al procesar el JSON"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
