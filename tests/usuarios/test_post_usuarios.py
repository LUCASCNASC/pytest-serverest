from services.usuarios.usuarios_post_service import usuarios

def test_usuarios_post_sucess():
    response = usuarios()
    body = response.json()

    assert response.status_code == 201
    assert body["message"] == "Cadastro realizado com sucesso"
    assert "_id" in body
