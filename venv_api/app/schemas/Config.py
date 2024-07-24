from pydantic import BaseModel

class Config(BaseModel):
    id: int | None
    id_emials: int
    pages_number: int
    contacts_number: int
    author: str
    email: str
    url: str
    comment: str
    subject: str
    message: str
    
class Emails(BaseModel):
    id: int | None
    email: str
    password: str