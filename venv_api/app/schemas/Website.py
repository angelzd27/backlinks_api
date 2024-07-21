from pydantic import BaseModel
from datetime import datetime

class Website(BaseModel):
    id: int | None
    url: str
    status: str | None
    created_at: datetime | None
    
class CommentRequest(BaseModel):
    keyword: str
    number_of_pages: int
    author: str
    email: str
    url: str
    comment: str