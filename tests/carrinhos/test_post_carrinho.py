from services.carrinhos.post_carrinho_service import criar_carrinho

def test_post_carrinho_success():
    response = criar_carrinho()
    body = response.json()

    assert response.status_code == 201
    assert body["message"] == "Cadastro realizado com sucesso"
    assert "_id" in body

