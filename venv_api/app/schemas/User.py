from pydantic import BaseModel

class User(BaseModel):
    id: int | None
    name: str
    last_name: str
    email: str
    password: str
    status: int | None
    
class UserLoginSchema(BaseModel):
    email: str
    password: str
    
class UserUpdate(BaseModel):
    id: str | None
    name: str
    last_name: str
    email: str