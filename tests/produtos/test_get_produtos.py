from services.produtos.produtos_get_service import get_produtos

def test_get_produtos_success():
    response = get_produtos()
    body = response.json()

    assert response.status_code == 200
    assert "quantidade" in body
    assert "produtos" in body
    assert isinstance(body["produtos"], list)
