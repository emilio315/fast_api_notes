from typing import Annotated
from fastapi import Depends, Path, HTTPException, APIRouter
from pydantic import BaseModel, Field
from models import User
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

bcrypt_contex = CryptContext(schemes=['bcrypt'], deprecated="auto")

class UserRequest(BaseModel):
    email:str = Field(min_length=3)
    username:str = Field(min_length=1, max_length=50)
    first_name:str = Field(min_length=1, max_length=50)
    last_name:str = Field(min_length=1, max_length=50)
    hashed_password:str = Field(min_length=8)
    role:str = Field(min_length=3)

    model_config = {
        "json_schema_extra":{
            "example":{
                "email":"czavala@finkok.com",
                "username":"czavala@finkok.com",
                "first_name":"Carlos",
                "last_name":"Zavala",
                "hashed_password":"Password#",
                "role":"usuario"

            }
        }
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter(User.username==username).first()
    if not user:
        return False
    if not bcrypt_contex.verify(password, user.hashed_password):
        return False
    return True

@router.get("/auth/")
async def get_user():
    return {'user':'authenticated'}

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency ,user_request:UserRequest):
    new_user = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_contex.hash(user_request.hashed_password),
        is_active=True,
        role=user_request.role
    )
    db.add(new_user)
    db.commit()

@router.get("/users/")
async def read_all_users(db: db_dependency):
    return db.query(User).all()


@router.post("/token")
async def login_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]
                             , db: db_dependency):

    response = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not response:
        return {"Authentication failed"}
    return {"Authentication success"}
