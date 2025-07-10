from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import bcrypt
from database.sql import get_db
from models.user_model import User
from entities.user_entity import UserCreate, UserResponse, LoginRequest

router = APIRouter()

@router.get("/account/{user_id}", response_model=UserResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user =  db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/profile/{user_id}", response_model=UserResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user =  db.query(User).filter(User.USER_ID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.USER_EMAIL == user.USER_EMAIL).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 🔐 Hash password before storing
    hashed_pw = bcrypt.hashpw(user.USER_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        FIRST_NAME=user.FIRST_NAME,
        LAST_NAME=user.LAST_NAME,
        USER_EMAIL=user.USER_EMAIL,
        USER_PASSWORD=hashed_pw,
        COMPANY_NAME=user.COMPANY_NAME,
        COMPANY_DEPARTMENT=user.COMPANY_DEPARTMENT
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user_id": new_user.USER_ID}

@router.post("/users/login")
def login(req: LoginRequest,  db: Session = Depends(get_db)):
    user = db.query(User).filter(User.USER_EMAIL == req.USER_EMAIL).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not bcrypt.checkpw(req.USER_PASSWORD.encode('utf-8'), user.USER_PASSWORD.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"user_id": user.USER_ID}