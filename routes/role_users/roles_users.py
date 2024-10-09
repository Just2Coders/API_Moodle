from fastapi import APIRouter,HTTPException
from fastapi.responses import JSONResponse
from globals.Const import Xetid_token,MOODLE_URL,MOODLE_WS_ENDPOINT
import requests
role_user_router = APIRouter(prefix="/role_user",tags=["Todas las rutas que involucren ROLES"])
@role_user_router.post("/asignar_rol")
def asignar_rol_a_usuario(user_id:int,role_id:int,contextid:int):
    params = {
            'wstoken': Xetid_token,
            'wsfunction': 'core_role_assign_roles',
            'moodlewsrestformat': 'json',
            'assignments[0][roleid]': role_id,
            'assignments[0][userid]': user_id,
            'assignments[0][contextid]': contextid
        }
    print(contextid)
    response = requests.post(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params,ssl = False)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error al asignar el rol al usuario")
    return response.json()
