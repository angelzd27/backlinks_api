from pydantic import BaseModel
from datetime import datetime

class Contact(BaseModel):
    id: int | None
    url: str
    emails: str
    phones: str
    company_name: str
    created_at: datetime | None