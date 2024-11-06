import requests
from fastapi import APIRouter
from globals.Const import XETID_TOKEN,MOODLE_URL,MOODLE_WS_ENDPOINT 
competition_user_router = APIRouter(prefix="/Competition_user",tags=["Rutas que involucren relaciones de Competiciones con CURSOS "])
def create_competency(shortname, description):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_competency_create_competency',
        'shortname': shortname,
        'description': description,
        'moodlewsrestformat': 'json'
    }
    response = requests.post(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params)
    return response.json()
@competition_user_router.post("/competency/create")
def create_new_competency(shortname: str, description: str):
    result = create_competency(shortname, description)
    return result

  
    
@competition_user_router.get("/competency/scale_values")
def read_scale_values(scaleid:int):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_competency_get_scale_values',
        'moodlewsrestformat': 'json',
        "scaleid":scaleid
    }
    response = requests.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params)
    return response.json()
    
@competition_user_router.get("/grades")
def read_student_grades(courseid: int, userid: int):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'gradereport_user_get_grades_table',
        'courseid': courseid,
        'userid': userid,
        'moodlewsrestformat': 'json'
    }
    response = requests.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params)
    return response.json()
@competition_user_router.get("/user/{userid}/course/{courseid}/competencies")
def get_user_competencies_in_course(courseid, userid):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_competency_user_competency_viewed_in_course',
        'courseid': courseid,
        'userid': userid,
        'moodlewsrestformat': 'json'
    }
    response = requests.get(MOODLE_URL + MOODLE_WS_ENDPOINT, params=params)
    return response.json()
    
