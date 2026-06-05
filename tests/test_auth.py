from fastapi.testclient import TestClient

from app.models.user import User



# Registration
def test_register_success(client: TestClient):
    email = "newuser@example.com"
    password = "newpassword"
    data = {
        "email": email,
        "password": password
    }
    response = client.post("/register", json=data)
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_register_existing_user(client: TestClient, test_user: User):
    email = test_user.email
    password = "newpassword"
    data = {
        "email": email,
        "password": password
    }
    response = client.post("/register", json=data)
    assert response.status_code == 409

def test_register_bad_email(client: TestClient):
    email = "bad_email"
    password = "newpassword"
    data = {
        "email": email,
        "password": password
    }
    response = client.post("/register", json=data)
    assert response.status_code == 422


# Login
def test_login_success(client: TestClient, test_user: User):
    data = {
        "username": test_user.email,
        "password": "password123"
    }
    response = client.post("/token", data=data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user: User):
    data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post("/token", data=data)
    assert response.status_code == 401

def test_login_unknown_email(client: TestClient):
    data = {
        "username": "unknown@example.com",
        "password": "password123"
    }
    response = client.post("/token", data=data)
    assert response.status_code == 401

def test_login_empty_username(client: TestClient):
    data = {
        "username": "",
        "password": "password123"
    }
    response = client.post("/token", data=data)
    assert response.status_code == 422