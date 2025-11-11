from typing import Annotated
from fastapi import Depends, Path, HTTPException, APIRouter
from pydantic import BaseModel, Field
from models import ToDoTask
from database import SessionLocal
from sqlalchemy.orm import Session
from starlette import status


router = APIRouter()

class ToDoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=1, max_length=100)
    priority:int = Field(gt=0, lt=6)
    complete:int = Field()

    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"Lavar trastes",
                "description":"Lavar y secar los trastes",
                "priority":5,
                "complete":False
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

@router.get("/")
async def read_all_task(db: db_dependency):
    return db.query(ToDoTask).all()

@router.get("/todo/{todo_id}/",status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency,todo_id:int = Path(gt=0)):
    try:
        return db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()
    except:
        raise HTTPException(404, detail='Item not found')

@router.post("/create-todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency ,todo_request:ToDoRequest):
    new_todo = ToDoTask(**todo_request.model_dump())
    db.add(new_todo)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency ,
                      todo_request:ToDoRequest,
                      todo_id:int  = Path(gt=0)
                      ):
    todo_model = db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(404, detail='Item not found')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency ,
                      todo_id:int  = Path(gt=0)
                      ):
    todo_model = db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(404, detail='Item not found')

    db.delete(todo_model)
    db.commit()
