import random
import string
from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED
from ..config.database import connection
from ..models.persistence import configs
from ..schemas.Config import Config, Emails
from sqlalchemy.exc import IntegrityError
from auth.jwtbearer import JWTBearer
from sqlalchemy import text

config = APIRouter(tags=['config'])

@config.get("/get_config/{id}", dependencies=[Depends(JWTBearer())])
async def get_config(id):
    query = text("SELECT c.id, c.pages_number, c.contact_number, c.author, c.email AS config_email, c.url, c.comment, c.subject, c.message, JSON_ARRAYAGG(JSON_OBJECT('id', e.id, 'email', e.email, 'password', e.password)) AS related_emails FROM config c LEFT JOIN config_emails ce ON c.id = ce.id_config LEFT JOIN emails e ON ce.id_emails = e.id WHERE c.id = :id_config GROUP BY c.id")
    id_config = {
        "id_config": id
    }
    result = connection.execute(query, id_config).fetchall()
    return {"error": False, 'msg':result}

@config.post("/create_email_config", dependencies=[Depends(JWTBearer())])
async def create_config(request: Emails):
    try:
        query = text("CALL email_config(:id_config, :email, :password)")
        new_email = {
            "id_config": request.id,
            "email": request.email,
            "password": request.password
        }
        connection.execute(query, new_email)
        return {"error": False, 'msg': 'Email created'}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)