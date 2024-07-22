from typing import List, Tuple
from pydantic import BaseModel
from datetime import datetime

class Contact(BaseModel):
    id: int | None
    url: str
    emails: str
    phones: str
    company_name: str
    created_at: datetime | None
    
class ContactResponse(BaseModel):
    keyword: str
    number_of_pages: int
    
class EmailCredential(BaseModel):
    email: str
    password: str
    
class EmailSender(BaseModel):
    subject: str
    message: str
    credentials: List[EmailCredential]
    
# Como se debe enviar la petición:
# {
#   "subject": "FastAPI email",
#   "message": "Esto es una prueba desde fastAPI",
#   "credentials": [  
#       {"email": "angelzd27@gmail.com", "password": "xegc gkbo flep rhwk"},
#       {"email": "l.zada010425@itses.edu.mx","password": "Sistemas2022$"}
#   ]
# }