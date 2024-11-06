from fastapi.security import OAuth2PasswordBearer
MOODLE_URL = "https://preparatoria.xutil.cu"
MOODLE_COURSE_URL = MOODLE_URL+"/course/view.php?id="
Xetid_token = "a01d5df2494e4a56fdc79f6a3dffaf43"
# Admin_token = "33d51de128c8717fcbf5eac664dd7848"
MOODLE_WS_ENDPOINT = "/webservice/rest/server.php"
Xetid_marlon_token ="3ee63f9b64257bea14c8bf9c9912e086"
# local_url = "http://localhost:4000"
# xetid_url= "metnira"
SECRET_KEY = "Cualquiera"
MOODLE_LOGIN_ENDPOINT = "/login/token.php"
MOODLE_SERVICE = "miAPI"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/User/token")