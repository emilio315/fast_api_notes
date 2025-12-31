from .utils import *
from ..routers.admin import get_db, get_current_user
from starlette import status 



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get('/admin/todo')
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

def test_admin_delete_todo(test_todo):
    todo_id = 1
    response = client.delete(f"/admin/todo/{todo_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(ToDoTask).filter(ToDoTask.id == todo_id).first()

    assert model is None
