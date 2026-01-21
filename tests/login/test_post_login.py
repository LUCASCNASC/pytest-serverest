from services.login.login_post_service import login

def test_login_success():
    response = login()

    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "Login realizado com sucesso"
    assert "authorization" in body
    assert body["authorization"].startswith("Bearer ")
    
def test_login_email_invalido():
    response = login(
        email="email_invalido@qa.com",
        password="teste"
    )

    body = response.json()

    assert response.status_code == 401
    assert body["message"] == "Email e/ou senha inválidos"

def test_login_senha_invalida():
    response = login(
        email="fulano@qa.com",
        password="senha_errada"
    )

    body = response.json()

    assert response.status_code == 401
    assert body["message"] == "Email e/ou senha inválidos"