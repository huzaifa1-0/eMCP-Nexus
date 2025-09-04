from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    password_hash: str
    reputation: float = 0.0