from fastapi.testclient import TestClient

from modules.api import users_api_example

client = TestClient(users_api_example.router)


def test_read_main():
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == [{'username': 'Foo'}, {'username': 'Bar'}]
