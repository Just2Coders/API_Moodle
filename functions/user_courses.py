import aiohttp
from globals.Const import XETID_TOKEN,MOODLE_URL,MOODLE_WS_ENDPOINT

async def esta_matriculado(user_id, course_id):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'core_enrol_get_enrolled_users',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params) as response:
            enrolled_users = await response.json()

            # Verifica si el user_id está en la lista de usuarios matriculados
            for user in enrolled_users:
                if user["id"] == user_id:
                    return True
            return False


# Función para matricular automáticamente al usuario
async def matricular_usuario(user_id, course_id):
    params = {
        'wstoken': XETID_TOKEN,
        'wsfunction': 'enrol_manual_enrol_users',
        'moodlewsrestformat': 'json',
        'enrolments[0][roleid]': 5,  # Estudiante
        'enrolments[0][userid]': user_id,
        'enrolments[0][courseid]': course_id
    }

    async with aiohttp.ClientSession() as session:
        await session.post(MOODLE_URL+MOODLE_WS_ENDPOINT, params=params)
           