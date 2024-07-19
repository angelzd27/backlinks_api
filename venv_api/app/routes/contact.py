from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from ..config.database import connection
from ..models.persistence import contacts
from ..schemas.Contact import Contact
from sqlalchemy import text

contact = APIRouter(tags=['contact'])