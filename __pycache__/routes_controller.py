import jwt
import time
from globals.variables import MOODLE_COURSE_URL
SECRET_KEY = "tu_clave_secreta"
MOODLE_URL = MOODLE_COURSE_URL+"?id="

def generar_url_segura(course_id, user_id):
    # Genera un token con la información del curso y usuario
    payload = {
        "course_id": course_id,
        "user_id": user_id,
        "exp": time.time() + 300  # Expiración en 5 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    # URL protegida con el token como parámetro
    url_protegida = f"{MOODLE_URL}{course_id}?token={token}"
    return url_protegida