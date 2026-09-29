from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.api import users_api_example


app = FastAPI()
app.include_router(users_api_example.router)

client = TestClient(app)


def test_read_main():
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == [
        {"username": "Foo"},
        {"username": "Bar"},
    ]