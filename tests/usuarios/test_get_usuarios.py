from services.usuarios.usuarios_get_service import get_usuarios

def test_get_usuarios_success():
    response = get_usuarios()
    body = response.json()

    assert response.status_code == 200
    assert "quantidade" in body
    assert "usuarios" in body
    assert isinstance(body["usuarios"], list)
