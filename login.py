from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
import requests
from datetime import datetime, timedelta
import urllib.parse

# Secret key para JWT
SECRET_KEY = "mi_secreto_super_seguro"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake database
fake_users_db = {
    "user@example.com": {
        "username": "pruebasincontext",
        "email": "string2321@gmail.com",
        "hashed_password": "$2b$12$eYB7P4OwYq2U.AiytwWf7.X8hZX5.x56dXTnMdopPSYAE3iS9.FFq",  # bcrypt hash de 'password123'
        "disabled": False,
    }
}

# Contexto para manejar el hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme para manejar tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str
# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Endpoint para obtener el token (usado por Moodle)
# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=400, detail="Usuario o contraseña incorrectos"
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# Función para validar el token

# Funciones auxiliares para manejar contraseñas y usuarios

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, email: str, password: str):
    user = get_user(fake_db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user
# Endpoint /token ajustado para recibir un authorization_code
@app.post("/oauth/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    redirect_uri: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    # Validar el client_id y el client_secret (esto debe coincidir con lo que Moodle envía)
    print(redirect_uri)
    print(grant_type)
    print(code)
    if client_id != "fastapi-client-id" or client_secret != "fastapi-client-secret":
        raise HTTPException(status_code=400, detail="Invalid client credentials")
    
    # Verificamos si el código de autorización es válido (simulado en este caso)
    if code != "autorizacionconcedida":
        raise HTTPException(status_code=400, detail="Invalid authorization code")
    
    # Generamos el token JWT para Moodle
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": "pruebasincontext@example.com"},  # Aquí debería estar el usuario autenticado
        expires_delta=access_token_expires
    )
    
    # Devolvemos el access token
    return {"access_token": access_token, "token_type": "bearer"}

#

# Endpoint de autorización
@app.get("/oauth/authorize")
async def authorize(client_id: str, redirect_uri: str, response_type: str, scope: str, state: str):
    print(scope)
    print(redirect_uri)
    print(response_type)
    print(state)
    print(client_id)
   
    

    if client_id != "fastapi-client-id":
        raise HTTPException(status_code=400, detail="Invalid client ID")
    print(redirect_uri)
    # Simulamos la autenticación y generamos un código de autorización
    authorization_code = "autorizacionconfcedida"
    # decoded_state = urllib.parse.unquote(state)
    print("state igual")
    print(state)
    # redirect = "https://docs.moodle.org/dev/"
    # state = urllib.parse.quote(state, safe='')
    # Redirigimos de vuelta a Moodle con el código de autorización y el estado original
    redirect_url = f"{redirect_uri}?code={authorization_code}&state={state}&response_type=code"
    return RedirectResponse(url=redirect_url, status_code=301)

     

# Endpoint para obtener información del usuario
@app.get("/oauth/user_info")
async def user_info(token: str = Depends(oauth2_scheme)):
    print(token)
    user = await get_current_user(token)
    return {"email": user.email}
@app.get("/.well-known/openid-configuration")
async def exploration(request):
    print(request)

@app.post("/login")
async def login():
    login_url = 'https://preparatoria.xutil.cu/login/index.php'

    payload = {
    'username': 'admin_xetid',
    'password': 'Xetid2019*'
    }

    session = requests.Session()
    response = session.post(login_url, params=payload, verify=False)

    if "loginerror" not in response.text:
        print("Autenticación exitosa")
        resp = RedirectResponse(url="https://preparatoria.xutil.cu")
        cook = response.cookies.get("MoodleSession")
        resp.set_cookie(key="MoodleSession", value=cook)
        return JSONResponse(content={"data":{"url":"https://preparatoria.xutil.cu","MoodleSession":cook, "path":"/" }, "message":"Ok" }, status_code=200)
    else:
        print("Error en la autenticación")
        return JSONResponse(content={"data":None, "message":"Unauthorized" }, status_code=401)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
