import random
import string
from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED
from ..config.database import connection
from ..models.persistence import users
from ..schemas.User import User, UserLoginSchema, UserUpdate
from ..helpers.bcrypt_helper import hash_password
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from auth.jwthandler import signJWT
from auth.jwtbearer import JWTBearer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

user = APIRouter(tags=['users'])

@user.post("/login")
async def login(userLogin: UserLoginSchema):
    
    result = connection.execute(users.select().where(users.c.email == userLogin.email)).first()
    
    print(result)

    if result == None:
        return {'error': True, 'msg': 'Not Logged'}
    
    if check_password_hash(password=userLogin.password, pwhash=result.password):
        data = {
                "id" : result.id,
                "name" : result.name,
                "last_name": result.last_name,
                "email" : result.email,
                "id_profile" : result.id_profile
            }
        token = signJWT(data)
        return { 'error': False, 'msg': 'You are logged!', 'token': token['access_token']}

    return {'error': True, 'msg': result}

@user.get('/get_users', dependencies=[Depends(JWTBearer())])
async def get_users():
    result = connection.execute("SELECT * FROM users WHERE status = 1").fetchall()
    if result == None:
        return {'error': True, 'msg': 'There are not users'}
    return {"error": False, 'msg':result}

# Get user by id
@user.get('/get_user_by_id/{id}', dependencies=[Depends(JWTBearer())])
async def get_user_by_id(id):
    result = connection.execute(users.select().where(users.c.id == id, users.c.status == 1)).first()
    if result != None:
        _status = status.HTTP_200_OK
        return {"error":False,"msg":result}
    _status = status.HTTP_404_NOT_FOUND

    result = {"error":True,"msg":"User not found"}
    return JSONResponse(status_code=_status, content=result)

def id_generator():
    characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    random_string = ''.join(random.choice(characters) for _ in range(18))
    
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    
    return formatted_time + random_string

# Add new user
@user.post('/create_user')
async def create_user(user: User):
    try:
        new_password = generate_password_hash(user.password, "pbkdf2", 30)
        query = text('CALL user_register(:name, :last_name, :email, :password, :id_profile)')
        new_user = {
            "name": user.name,
            "last_name" : user.last_name,
            "email": user.email,
            "password": new_password,
            "id_profile": user.id_profile
        }
        connection.execute(query, new_user)
        return {"error":False,"msg":"User created"}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)

# Update password by email
@user.put('/update_password')
async def update_user(user: UserLoginSchema):
    try:
        new_password = generate_password_hash(user.password, "pbkdf2", 30)
        connection.execute(users.update().values(password=new_password).where(users.c.email == user.email)).last_updated_params()

        _status = status.HTTP_200_OK
        result = {"error":False, "msg":"Password updated"}
        return JSONResponse(status_code=_status, content=result)
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)
    
# Update user by id
@user.put('/update_user/{id}', dependencies=[Depends(JWTBearer())])
async def update_user(id, userUpdate: UserUpdate):
    try:
        connection.execute(users.update().values(name=userUpdate.name, last_name=userUpdate.last_name, email=userUpdate.email).where(users.c.id == id)).last_updated_params()

        _status = status.HTTP_200_OK
        result = {"error":False, "msg":"User updated"}
        return JSONResponse(status_code=_status, content=result)
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)

# Ruta para eliminar usuarios por su id
@user.delete('/delete_user/{id}', dependencies=[Depends(JWTBearer())])
async def delete_user(id):
    try:
        connection.execute(users.update().values(status=0).where(users.c.id == id)).last_updated_params()
        _status = status.HTTP_200_OK
        result = {"error":False, "Mgs":"User deleted"}
        return JSONResponse(status_code=_status, content=result)
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[1], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)