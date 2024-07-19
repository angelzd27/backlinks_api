from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from ..config.database import connection
from ..models.persistence import websites
from ..schemas.Website import Website
from sqlalchemy import text

website = APIRouter(tags=['website'])