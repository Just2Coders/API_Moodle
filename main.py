from fastapi import FastAPI, Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import JSONResponse
from globals.Const import local_url
# import httpx
from models.token_model import Token
from globals.Const import MOODLE_URL
from routes.course_user_relations.course_user_relations import course_user_router
from routes.courses.courses import courses_router
from routes.role_users.roles_users import role_user_router
from routes.users.users import user_router
from routes.competitions.competition import competition_user_router
import requests
import json

app = FastAPI()
app.description = "Mi capacitation page"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.include_router(course_user_router)
app.include_router(user_router)
app.include_router(role_user_router)
app.include_router(courses_router)
app.include_router(competition_user_router)
# class User(BaseModel):
#     username:str
#     password:str
#     firstname: str
#     lastname: str
#     email: str
#     auth:str
#     createpassword: int
#     roleid:int = 5
#     contextid:int = 1



# @app.post("/registrar_usuario")
# def registrar_usuario(user: User):
#     url = f"{MOODLE_URL}/webservice/rest/server.php?"
#     # 53 hasta 71 noooo
#     # users = [{
#     #     'username': user.username,
#     #     'password': user.password,
#     #     'firstname': user.firstname,
#     #     'lastname': user.lastname,
#     #     'email': user.email,
#     #     'auth': user.auth,
#     #     'createpassword':user.createpassword
#     # }, ]
#     # params = {
#     #     'wstoken': Xetid_token,
#     #     'wsfunction': 'core_user_create_users',
#     #     'moodlewsrestformat': 'json',
#     #     'users' : users[0]
    
#     # }
   
#     # print(users)
#     response = requests.post(f"{url}wstoken={Xetid_token}&wsfunction=core_user_create_users&moodlewsrestformat=json&users[0][username]={user.username}&users[0][password]={user.password}&users[0][firstname]={user.firstname}&users[0][email]={user.email}&users[0][lastname]={user.lastname}&users[0][auth]={user.auth}")
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error al crear el usuario en Moodle")
#     data = response.json()
#     print(data)
#     return(data)
#     # print(user.roleid)
#     # roleuser= assign_role_to_user(data[0]["id"], user.roleid,user.contextid)
#     # print(roleuser)
#     # return roleuser
# # @app.post("/login/{user}/{password}/{function}")
# # async def LOGIN(user:str,password:str,function:str):
# #     print(function)
# #     response = requests.post(f"http://localhost:4000/login/token.php?username={user}&password={password}&service={function}")
# #     if response.status_code != 200:
# #         raise HTTPException(status_code=response.status_code, detail="Error al loguearse")
# #     return response.json()
# @app.get("/mi-ip")
async def obtener_ip_cliente(request: Request):
    ip_cliente = request.client.host
    return {"ip_cliente": ip_cliente}

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

# def get_moodle_courses():
#     params = {
#         'wstoken': Xetid_token,
#         'wsfunction': 'core_course_get_courses',
#         'moodlewsrestformat': 'json'
#     }
#     response = requests.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Error al obtener los cursos")
#     return response.json()

# @app.get("/courses")
# async def read_courses():

#     courses = get_moodle_courses()
#     return courses

# @app.get("/courses/search")
# async def search_courses(query: str):
#     courses = get_moodle_courses()
#     filtered_courses = [course for course in courses if query.lower() in course['fullname'].lower()]
#     return filtered_courses
# @app.post("/matricular")
# def enrol_user_in_course(userid:str, courseid:int, roleid:int = 0):
#     params = {
#         'wstoken': Xetid_token,
#         'wsfunction': 'enrol_manual_enrol_users',
#         'moodlewsrestformat': 'json',
#         'enrolments[0][roleid]': roleid,
#         'enrolments[0][userid]': userid,
#         'enrolments[0][courseid]': courseid
#     }
#     response = requests.post(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Error al inscribir al usuario en el curso")
#     return response.json()
# @app.post("/get_users_in_course")
# def get_users_in_course(course_id:int):
#     url = MOODLE_URL + MOODLE_WS_ENDPOINT
#     token = Xetid_token
#     function = "core_enrol_get_enrolled_users"

#     params = {
#         "wstoken": token,
#         "wsfunction": function,
#         "moodlewsrestformat": "json",
#         "courseid": course_id  # Reemplaza course_id con el ID del curso
#     }

#     response = requests.post(url, data=params)
#     enrolled_users = response.json()
#     print(enrolled_users)
#     return enrolled_users
# @app.post("/asignar_rol")
# def asignar_rol_a_usuario(user_id:int,role_id:int,contextid:int):
#     roleuser= assign_role_to_user(user_id,role_id ,contextid)
#     print(roleuser)
#     return roleuser
# def assign_role_to_user(userid:int, roleid:int,contextid:int|None = None):
#     params = {
#         'wstoken': Xetid_token,
#         'wsfunction': 'core_role_assign_roles',
#         'moodlewsrestformat': 'json',
#         'assignments[0][roleid]': roleid,
#         'assignments[0][userid]': userid,
#         'assignments[0][contextid]': contextid
#     }
#     print(contextid)
#     response = requests.post(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params)
#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Error al asignar el rol al usuario")
#     return response.json()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
