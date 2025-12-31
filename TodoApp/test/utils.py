from sqlalchemy import create_engine, text
from sqlalchemy import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from ..database import Base
from ..models import ToDoTask
from ..main import app
import pytest


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {
    "id": 1,
    "role": "admin",
    "username": "czavala@finkok.com"
    }

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = ToDoTask(
        title="Lavar la ropa",
        description ="Lavar y tender la ropa",
        priority=4,
        complete=False,
        owner_id = 1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todostask;"))
        connection.commit()