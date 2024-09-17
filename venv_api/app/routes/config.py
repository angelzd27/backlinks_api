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
# Comment Here
async def get_config(id):
    query = text('''
    SELECT 
        c.id, 
        c.pages_number, 
        c.contact_number, 
        c.author, 
        c.email AS config_email, 
        c.url, 
        c.comment, 
        c.subject, 
        c.message, 
        IFNULL(
            (
                SELECT 
                    CONCAT('[', 
                    GROUP_CONCAT(
                        CONCAT(
                            '{"id":', e.id, ', "email":"', e.email, '", "password":"', e.password, '"}'
                        )
                    ), 
                    ']') 
                FROM emails e 
                JOIN config_emails ce ON ce.id_emails = e.id 
                WHERE ce.id_config = c.id AND e.status = 1
            ), 
            '[]'
        ) AS related_emails 
    FROM config c 
    WHERE c.id = :id_config 
    GROUP BY c.id, c.pages_number, c.contact_number, c.author, config_email, c.url, c.comment, c.subject, c.message;
    ''')

    params = {"id_config": id}

    result = connection.execute(query, params).fetchall()

    return {"error": False, "msg": result}

@config.post("/create_email_config", dependencies=[Depends(JWTBearer())])
async def create_config(request: Emails):
    try:
        query = text("CALL email_config(:id_config, :email, :password)")
        new_email = {
            "id_config": request.id,
            "email": request.email,
            "password": request.password,
            "status": request.status,
        }
        connection.execute(query, new_email)
        return {"error": False, 'msg': 'Email created'}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)
    
@config.post("/edit_config", dependencies=[Depends(JWTBearer())])
async def edit_config(request: Config):
    try:
        query = text("UPDATE config SET pages_number = :pages_number, contact_number = :contacts_number, author = :author, email = :email, url = :url, comment = :comment, subject = :subject, message = :message WHERE id = :id")
        edit_config = {
            "id": request.id,
            "pages_number": request.pages_number,
            "contacts_number": request.contacts_number,
            "author": request.author,
            "email": request.email,
            "url": request.url,
            "comment": request.comment,
            "subject": request.subject,
            "message": request.message
        }
        connection.execute(query, edit_config)
        return {"error": False, 'msg': 'Configuration edited'}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)
    
@config.post("/edit_email", dependencies=[Depends(JWTBearer())])
async def edit_email(request: Emails):
    try:
        query = text("UPDATE emails SET email = :email, password = :password WHERE id = :id")
        edit_email = {
            "id": request.id,
            "email": request.email,
            "password": request.password
        }
        connection.execute(query, edit_email)
        return {"error": False, 'msg': 'Email edited'}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)
    
@config.delete("/delete_email/{id}", dependencies=[Depends(JWTBearer())])
async def delete_email(id):
    try:
        query = text("UPDATE emails SET status=0 WHERE id = :id")
        id_email = {
            "id": id
        }
        connection.execute(query, id_email)
        return {"error": False, 'msg': 'Email deleted'}
    except IntegrityError as exc:
        _status = status.HTTP_500_INTERNAL_SERVER_ERROR
        result = {"error": True, "err_code":exc.orig.args[0], "msg":"There's an error: " + exc.orig.args[1]}
        return JSONResponse(status_code=_status, content=result)
    