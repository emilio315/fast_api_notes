from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, Path
from pydantic import BaseModel, Field
from ..models import User
from ..database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

SECRET_KEY = '428fb56bb6de39905ae9cf2cc840afddfe8277b586d124fe14a4fff5b3d2e7fe'

ALGORITHM = "HS256"

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_contex = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class UserRequest(BaseModel):
    email:str = Field(min_length=3)
    username:str = Field(min_length=1, max_length=50)
    first_name:str = Field(min_length=1, max_length=50)
    last_name:str = Field(min_length=1, max_length=50)
    hashed_password:str = Field(min_length=8)
    role:str = Field(min_length=3)
    phone_number:str = Field(min_length=3)

    model_config = {
        "json_schema_extra":{
            "example":{
                "email":"czavala@finkok.com",
                "username":"czavala@finkok.com",
                "first_name":"Carlos",
                "last_name":"Zavala",
                "hashed_password":"Password#",
                "role":"usuario",
                "phone_number":"4433161903"

            }
        }
    }

class UpdateUserRequest(BaseModel):
    phone_number:str = Field(min_length=3)

    model_config = {
        "json_schema_extra":{
            "example":{
                "phone_number":"4433161903"

            }
        }
    }

class Token(BaseModel):
    access_token:str
    token_type:str

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
    return user

def create_access_token(username:str,user_id:int, expires_date:timedelta):
    encode = {'sub':username, "id":user_id}
    expires = datetime.now(timezone.utc) + expires_date
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username :str = payload.get('sub')
        user_id:int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user')
        return {'username':username, 'id':user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user')


@router.post("/user/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency ,user_request:UserRequest):
    new_user = User(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_contex.hash(user_request.hashed_password),
        is_active=True,
        role=user_request.role,
        phone_number = user_request.phone_number
    )
    db.add(new_user)
    db.commit()

@router.put("/user/update/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
                      db: db_dependency ,
                      user_request:UpdateUserRequest,
                      user_id:int  = Path(gt=0)
                      ):

    user_model = db.query(User).filter(User.id == user_id).first()
    if user_model is None:
        raise HTTPException(404, detail='Item not found')

    # user_model.email = user_request.email
    # user_model.first_name = user_request.first_name
    # user_model.last_name = user_request.last_name
    user_model.phone_number = user_request.phone_number
    # user_model.role = user_request.role

    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()]
                             , db: db_dependency):

    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='could not validate user')
    token = create_access_token(
        user.username,
        user.id,
        timedelta(minutes=20))
    return {'access_token':token, 'token_type':'bearer'}
