from services.login_service import login

def test_login_success():
    response = login()

    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "Login realizado com sucesso"
    assert "authorization" in body
    assert body["authorization"].startswith("Bearer ")
