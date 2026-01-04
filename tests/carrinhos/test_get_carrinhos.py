from services.carrinhos.carrinhos_get_service import get_carrinhos


def test_get_carrinhos_success():
    response = get_carrinhos()
    body = response.json()

    assert response.status_code == 200
    assert "quantidade" in body
    assert "carrinhos" in body
    assert isinstance(body["carrinhos"], list)
