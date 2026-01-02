from services.users_service import get_users

def test_get_users_success():
    response = get_users()

    assert response.status_code == 200
    assert isinstance(response.json(), list)
