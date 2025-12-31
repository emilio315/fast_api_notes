from starlette import status 
from ..routers.todos import get_db, get_current_user
from ..models import ToDoTask
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'complete': False,
            'id': 1,
            'priority': 4,
            'title': 'Lavar la ropa',
            'description': 'Lavar y tender la ropa',
            'owner_id': 1
        }
    ]

def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
            'complete': False,
            'id': 1,
            'priority': 4,
            'title': 'Lavar la ropa',
            'description': 'Lavar y tender la ropa',
            'owner_id': 1
        }

def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todo/8211/")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
           "detail": "Item not found"
        }

def test_create_todo(test_todo):
    request_json = {
                "title":"Prueba",
                "description":"Probar pytest",
                "priority":5,
                "complete":False
            }
    response = client.post("/create-todo", json=request_json)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(ToDoTask).filter(ToDoTask.id == 2).first()

    assert model.title == request_json.get('title')
    assert model.description == request_json.get('description')
    assert model.priority == request_json.get('priority')
    assert model.complete == request_json.get('complete')

def test_update_todo(test_todo):
    request_json = {
            'complete': True,
            'priority': 4,
            'title': 'Cocinar',
            'description': 'Cocinar la cena',
            'owner_id': 1
        }
    todo_id = 1
    response = client.put(f"/todo/{todo_id}", json=request_json)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()

    assert model.title == request_json.get('title')
    assert model.description == request_json.get('description')
    assert model.priority == request_json.get('priority')
    assert model.complete == request_json.get('complete')

def test_update_todo_not_found(test_todo):
    request_json = {
            'complete': True,
            'priority': 4,
            'title': 'Cocinar',
            'description': 'Cocinar la cena',
            'owner_id': 1
        }
    todo_id = 2
    response = client.put(f"/todo/{todo_id}", json=request_json)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Item not found'}


def test_delete_todo(test_todo):
    todo_id = 1
    response = client.delete(f"/todo/{todo_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()

    assert model is None

def test_delete_todo_not_found(test_todo):
    todo_id = 2
    response = client.delete(f"/todo/{todo_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Item not found'}
