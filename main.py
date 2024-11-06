from fastapi import FastAPI, Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
from bs4 import BeautifulSoup
from typing import Annotated
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse
from jose import jwt,JWTError
from globals.Const import MOODLE_URL,MOODLE_COURSE_URL,SECRET_KEY,Xetid_token
from routes.course_user_relations.course_user_relations import course_user_router
from routes.courses.courses import courses_router
from routes.role_users.roles_users import role_user_router
from routes.users.users import user_router
from routes.competitions.competition import competition_user_router
from models.token_model import Token
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, Response, Depends
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, HTTPException
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
    allow_origins=["*"],  # Solo permitir orígenes de confianza
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
app.include_router(course_user_router)
app.include_router(user_router)
app.include_router(role_user_router)
app.include_router(courses_router)
app.include_router(competition_user_router)





MOODLE_LOGIN_URL = "https://preparatoria.xutil.cu/login/index.php"
MOODLE_COURSE_URL = "https://preparatoria.xutil.cu/course/view.php?id=7"

# @app.post("/login_and_redirect")
# async def login_and_redirect(username:str,password:str):
#     # Verificar las credenciales del usuario en tu sistema

#     async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
#         # Realiza el login en Moodle
#         login_payload = {
#             'username': username,
#             'password': password
#         }

#         # Enviar la solicitud de inicio de sesión a Moodle
#         async with session.post(MOODLE_LOGIN_URL, params=login_payload,ssl=False) as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=401, detail="Error al iniciar sesión en Moodle")
#             text = await response.text()
#             print(text)
#             cookies_response_1= response.cookies.values()
#             print(cookies_response_1)
#             cookies_response = response.cookies
#             # set_cookie_headers = []
#             redirectresponse = RedirectResponse(url=MOODLE_COURSE_URL)
#             for cookie in cookies_response.values():
#                 redirectresponse.set_cookie(key=cookie.key,value=cookie.value,domain=cookie['domain'],path=cookie['path'],secure=cookie['secure'])
#                 print(cookie.key)
#                 print(cookie.value)
#                 print(cookie['domain'])
#                 print(cookie['path'])
#                 print(cookie['secure'])
                
#             return redirectresponse
            # Procesa las cookies detalladas desde la respuesta
            # for cookie in cookies_response.values():
            #     cookie_string = f"{cookie.key}={cookie.value}"
            #     if cookie.get('domain'):
            #         cookie_string += f"; Domain={cookie['domain']}"
            #     if cookie.get('path'):
            #         cookie_string += f"; Path={cookie['path']}"
            #     if cookie.get('secure'):
            #         cookie_string += "; Secure"
            #     if cookie.get('httponly'):
            #         cookie_string += "; HttpOnly"
            #     if cookie.get('expires'):
            #         cookie_string += f"; Expires={cookie['expires']}"
                
            #     # Agrega la cookie al encabezado 'Set-Cookie'
            #     set_cookie_headers.append(("Set-Cookie", cookie_string))

            # Redirige al curso en Moodle con las cookies establecidas
            
    #         print("cookiesssssssssssss")
    #         print(cookies.values())
    #         values = cookies.values()  
    #         for cookie in cookies.values():
    # #             # Crear un encabezado 'Set-Cookie' para cada cookie de la sesión
    #             cookiesjson = {f'{cookie.key}':cookie.value} 
    #         print(cookiesjson)               
    #             # Crear un encabezado 'Set-Cookie' para cada cookie de la sesió         
    #         return RedirectResponse(url=MOODLE_COURSE_URL, headers={"Set-Cookie": cookiesjson})
            # return HTMLResponse(text)
    #         print(text)  # Obtener todas las cookies devueltas por Moodle
    #         cookies = session.cookie_jar.filter_cookies(MOODLE_LOGIN_URL)

    #         # Preparar las cookies para enviar al cliente
    #         set_cookie_headers = []
    #         for cookie in cookies.values():
    #             # Crear un encabezado 'Set-Cookie' para cada cookie de la sesión
    #             set_cookie_headers.append(f"{cookie.key}={cookie.value}; Path={cookie['path']}; HttpOnly; Secure;")

    # # Redirigir al usuario a la URL del curso de Moodle, incluyendo las cookies
    # return RedirectResponse(url=MOODLE_COURSE_URL, headers={"Set-Cookie": set_cookie_headers})
    
# app = FastAPI()

@app.post("/login_key")
async def login_key(email:str):
    params = {
        'wstoken': Xetid_token,
        'wsfunction': 'auth_userkey_request_login_url',
        'moodlewsrestformat': 'json',
        'user[email]': email
    }
    posteo = requests.post("https://preparatoria.xutil.cu/webservice/rest/server.php",params=params,verify=False)
    return  posteo.content
@app.post("/course")
async def course():
    course = requests.post(url="https://preparatoria.xutil.cu/auth/userkey/login.php?key=93fd62bfbe9daf0d90c0d2e13e1bbd30&wantsurl=https://preparatoria.xutil.cu/course/view.php?id=7",verify=False)
    print(course)
    return HTMLResponse(content=course.content)
@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="https://fastapi.tiangolo.com")
# @app.post("/login")
# async def login():
#     login_url = 'https://preparatoria.xutil.cu/login/index.php'

#     # Paso 1: Hacer una solicitud GET para obtener el token
#     response = requests.get(login_url, verify=False)
    
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error al conectar con Moodle")

#     # Paso 2: Analizar el HTML y extraer el token
#     soup = BeautifulSoup(response.content, 'html.parser')
#     token_input = soup.find('input', {'name': 'logintoken'})
    
#     if not token_input:
#         raise HTTPException(status_code=500, detail="No se pudo encontrar el token de inicio de sesión")

#     logintoken = token_input['value']

#     # Paso 3: Preparar el payload con el token
#     payload = {
#         'username': 'admin_xetid',
#         'password': 'Xetid2019*',
#         'logintoken': logintoken  # Agregar el token al payload
#     }

#     # Realizar la solicitud POST a Moodle
#     response = requests.post(login_url, data=payload, verify=False)

#     # Comprobar el código de estado de la respuesta
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error al conectar con Moodle")

#     # Comprobar el contenido de la respuesta para determinar si el inicio de sesión falló
#     if "Incorrect login or password" in response.text:
#         raise HTTPException(status_code=401, detail="Credenciales incorrectas")

#     # Si todo está bien, retornar el contenido de la respuesta
#     return HTMLResponse(content=response.content)
    # if "loginerror" not in response.text:
    #     print("Autenticación exitosa")
    #     resp = RedirectResponse(url="https://preparatoria.xutil.cu")
    #     cook = response.cookies.get("MoodleSession")
    #     resp.set_cookie(key="MoodleSession", value=cook)
    #     return JSONResponse(content={"data":{"url":"https://preparatoria.xutil.cu","MoodleSession":cook, "path":"/" }, "message":"Ok" }, status_code=200)
    # else:
    #     print("Error en la autenticación")
    #     return JSONResponse(content={"data":None, "message":"Unauthorized" }, status_code=401)
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

# # # Datos de usuario para login (ajusta con los datos correctos)
# MOODLE_USERNAME = "admin_xetid"
# MOODLE_PASSWORD = "Xetid2019*"

# @app.post("/login_cookies")
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
#         print(cookies)

#         async with session.post(LOGIN_URL, params=login_data, cookies=cookies,ssl =False) as login_response:
#             if login_response.status != 200:
#                 raise HTTPException(status_code=login_response.status, detail="Error al intentar autenticar")
#             print(cookies)
#             # print(await login_response.content.read())
#             print(login_response.url)
#             # Verificamos si el login fue exitoso
#             if 'login/index.php' in str(login_response.url):
#                 return {"detail": "Error de autenticación. Verifica las credenciales."}
            
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
