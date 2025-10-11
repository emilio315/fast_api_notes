from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
    id:int
    title:str
    author:str
    description:str
    rating:int
    published_date:int


    def __init__(self, id,title,author,description,rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id:Optional[int] = Field(description='ID is not needed on create',default=None)
    title:str = Field(min_length=3)
    author:str = Field(min_length=3)
    description:str = Field(min_length=1, max_length=100)
    rating:int = Field(gt=0, lt=6)
    published_date:int = Field()

    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"New book",
                "author":"J.K Rowlin",
                "description":"Descripcion de libro",
                "rating":5,
                "published_date":2019
            }
        }
    }

BOOKS = [
    Book(1,
         "Don Quijote de la Mancha",
         "Miguel de Cervantes",
         "Clasico de todos los tiempos",
         5,
         "2013"),
    Book(2,
         "Harry Potter y la piedra filosofal",
         "J.K. Rowling",
         "Clasico de todos los tiempos",
         5,
         "2011"),
    Book(3,
         "El Principito",
         "Antoine de Saint-Exupery",
         "Clasico de todos los tiempos",
         2,
         "2000"),
    Book(4,
         "Cien años de soledad",
         "Gabriel García Marquez",
         "Clasico de todos los tiempos",
         5,
         "2009")

]

@app.get("/books")
async def read_all_books():
    return BOOKS


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request:BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

def find_book_id(book:Book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id +1
    return book

@app.get("/books/{book_id}/")
async def read_book(book_id:int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(404, detail='Item not found')
        
@app.get("/books/")
async def read_book_by_rating(book_rating:int = Query(gt=0, lt=6)):
    book_list = []
    for book in BOOKS:
        if book.rating == book_rating:
            book_list.append(book)
    return book_list

@app.get("/books/date/")
async def read_book_by_date(book_date:int):
    book_list = []
    for book in BOOKS:
        if book.published_date == book_date:
            book_list.append(book)
    return book_list

@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request:BookRequest):
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i].id = book_request
            book_change = True
    if not book_change:
        raise HTTPException(404, detail='Item not found')


@app.delete("/books/delete/{book_id}/",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id:int = Path(gt=0)):
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_change = True
            break
    if not book_change:
        raise HTTPException(404, detail='Item not found')
