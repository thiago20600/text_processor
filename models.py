from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SummarySave(BaseModel):
    summary: str
    key_points: str
    questions: str
    title: Optional[str] = None
