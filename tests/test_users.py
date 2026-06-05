from fastapi.testclient import TestClient

from app.models.user import User



# GET
def test_get_user_success(auth_client: TestClient, test_user: User):
    response = auth_client.get("/users/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == test_user.email
    assert user_data["id"] == test_user.id
    assert user_data["is_active"] == test_user.is_active


# UPDATE
def test_update_user_success(auth_client: TestClient):
    new_email = "updated@example.com"
    data = {
        "email": new_email
    }
    response = auth_client.patch("/users/me", json=data)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == new_email

def test_update_email_conflict(auth_client: TestClient, second_test_user: User):
    data = {
        "email": second_test_user.email
    }
    response = auth_client.patch("/users/me", json=data)
    assert response.status_code == 409

def test_update_bad_password(auth_client: TestClient):
    data = {
        "password": "123"
    }
    response = auth_client.patch("/users/me", json=data)
    assert response.status_code == 422


# DELETE + GET
def test_delete_success(auth_client: TestClient):
    response = auth_client.delete("/users/me")
    assert response.status_code == 204
    # Testing if we can no longing access the endpoint
    response = auth_client.get("/users/me")
    assert response.status_code == 401