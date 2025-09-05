from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

router = APIRouter()


class UserLogin(BaseModel):
    email: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
async def register_user(user: UserRegister) -> dict:
    # TODO: Add real DB storage + hashing
    return {"message": f"User {user.username} registered successfully!"}

@router.post("/login")
async def login_user(user: UserLogin) -> dict:
    # TODO: Add real JWT + DB lookup
    if user.email == "demo@test.com" and user.password == "password":
        return {"token": "fake-jwt-token"}
    raise HTTPException(status_code=401, detail="Invalid credentials")