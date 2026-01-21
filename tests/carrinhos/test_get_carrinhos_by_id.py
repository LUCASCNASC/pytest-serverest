from services.carrinhos.carrinhos_post_service import criar_carrinho
from services.carrinhos.carrinhos_get_by_id_service import get_carrinhos_by_id

def test_get_carrinhos_by_id_success():
    post_response = criar_carrinho()
    post_body = post_response.json()

    carrinho_id = post_body["_id"]

    get_response = get_carrinhos_by_id(carrinho_id)
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["_id"] == carrinho_id

    assert "produtos" in body
    assert isinstance(body["produtos"], list)
    assert len(body["produtos"]) > 0

    assert "idProduto" in body["produtos"][0]