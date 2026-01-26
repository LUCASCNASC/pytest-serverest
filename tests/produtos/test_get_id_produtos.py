from services.produtos.produtos_get_id_service import get_id_produtos

def test_get_produto_por_id_success():
    response = get_id_produtos(1)
    body = response.json()

    assert response.status_code == 200

    # Valida que é um produto único, não lista
    assert "nome" in body
    assert "preco" in body
    assert "descricao" in body
    assert "_id" in body