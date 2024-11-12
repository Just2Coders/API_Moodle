import os
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
load_dotenv()
MOODLE_URL = "https://preparatoria.xutil.cu"
MOODLE_COURSE_URL = MOODLE_URL+"/course/view.php?id="
XETID_TOKEN = os.getenv('XETID_TOKEN')
MOODLE_WS_ENDPOINT = "/webservice/rest/server.php"
XETID_MARLON_TOKEN = os.getenv('XETID_MARLON_TOKEN')
MOODLE_LOGIN_ENDPOINT = "/login/token.php"
MOODLE_SERVICE = "miAPI"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/User/token",auto_error=False)
API_KEY_NAME = "access_token"
# local_url = "http://localhost:4000"
# xetid_url= "metnira"
# SECRET_KEY = "Cualquiera"
# Admin_token = "33d51de128c8717fcbf5eac664dd7848"