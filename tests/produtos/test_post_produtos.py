from services.produtos.produtos_post_service import produtos

def test_produtos_post_sucess():
    response = produtos()
    body = response.json()

    assert response.status_code == 201
    assert body["message"] == "Cadastro realizado com sucesso"
    assert "_id" in body
    