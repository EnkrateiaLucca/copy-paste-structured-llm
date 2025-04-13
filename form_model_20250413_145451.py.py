from pydantic import BaseModel
from typing import Optional

class ContactInformation(BaseModel):
    question: str
    email: str
    address: str
    phone_number: Optional[str] = None
    comments: Optional[str] = None