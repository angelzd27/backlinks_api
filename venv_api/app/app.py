from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.contact import contact
from .routes.user import user
from .routes.website import website
from .routes.config import config

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*']
)

app.include_router(user)
app.include_router(website)
app.include_router(contact)
app.include_router(config)