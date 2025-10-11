from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/apiendopoint")
async def first_api():
    return {"message":"Hola mundo"}

BOOKS = [
  {
    "Nombre": "Cien años de soledad",
    "Autor": "Gabriel García Márquez",
    "Categoria": "Realismo Mágico"
  },
  {
    "Nombre": "1984",
    "Autor": "George Orwell",
    "Categoria": "Distopia"
  },
  {
    "Nombre": "El Principito",
    "Autor": "Antoine de Saint-Exupéry",
    "Categoria": "Fábula"
  },
  {
    "Nombre": "Harry Potter y la piedra filosofal",
    "Autor": "J.K. Rowling",
    "Categoria": "Fantasía"
  },
  {
    "Nombre": "Don Quijote de la Mancha",
    "Autor": "Miguel de Cervantes",
    "Categoria": "Clasico"
  }
]

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/book/{book_id}")
async def get_book(book_id):
    return {'dynamic_param':book_id}

# @app.get("/books/{book_title}")
# async def read_book(book_title:str):
#     for book in BOOKS:
#         if book.get('Nombre').casefold() == book_title.casefold():
#             return book
@app.get("/books/author/")
async def get_book_by_author_query(author:str):
    book_list = []
    for book in BOOKS:
        if book.get('Autor').casefold() == author.casefold():
            book_list.append(book)
            return book

@app.get("/books/{book_title}/")
async def read_book(book_title:str, book_category:str):
    book_list = []
    for book in BOOKS:
        if book.get('Nombre').casefold() == book_title.casefold() and book.get('Categoria').casefold() == book_category.casefold():
            book_list.append(book)
            return book

@app.get("/books/")
async def read_book_by_query(category:str):
    print(category)
    book_list = []
    for book in BOOKS:
        if book.get('Categoria').casefold() == category.casefold():
            book_list.append(book)
            return book
        
@app.post("/books/create")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
  
@app.put("/books/update_book")
async def update_book(update_book=Body()):
    for i in range(len(BOOKS)):
      if  BOOKS[i].get('Nombre').casefold() == update_book.get('Nombre').casefold():
          BOOKS[i] = update_book


@app.delete("/books/delete/{book_title}/")
async def delete_book(book_title:str):
    book_list = []
    for i in range(len(BOOKS)):
        if BOOKS[i].get('Nombre').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
