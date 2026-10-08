from collections.abc import Iterator
from uuid import uuid4

import pytest
import requests


REQUEST_TIMEOUT = 10


def response_json(response: requests.Response) -> dict:
    assert response.headers.get("Content-Type", "").startswith("application/json")
    return response.json()


def create_user(
    api: requests.Session, base_url: str, *, is_admin: bool = False
) -> dict[str, str]:
    user = {
        "nome": "Pytest User",
        "email": f"pytest-{uuid4().hex}@example.com",
        "password": "pytest-password",
        "administrador": str(is_admin).lower(),
    }
    response = api.post(
        f"{base_url}/usuarios", json=user, timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == 201, response.text
    user["_id"] = response_json(response)["_id"]
    return user


def login(
    api: requests.Session, base_url: str, user: dict[str, str]
) -> dict[str, str]:
    response = api.post(
        f"{base_url}/login",
        json={"email": user["email"], "password": user["password"]},
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code == 200, response.text
    return response_json(response)


@pytest.fixture
def regular_user(
    api: requests.Session, base_url: str
) -> Iterator[dict[str, str]]:
    user = create_user(api, base_url)
    try:
        yield user
    finally:
        deleted = api.delete(
            f"{base_url}/usuarios/{user['_id']}", timeout=REQUEST_TIMEOUT
        )
        assert deleted.status_code == 200, deleted.text


@pytest.fixture
def admin(
    api: requests.Session, base_url: str
) -> Iterator[dict[str, str]]:
    user = create_user(api, base_url, is_admin=True)
    try:
        user["token"] = login(api, base_url, user)["authorization"]
        yield user
    finally:
        deleted = api.delete(
            f"{base_url}/usuarios/{user['_id']}", timeout=REQUEST_TIMEOUT
        )
        assert deleted.status_code == 200, deleted.text


@pytest.fixture
def product(
    api: requests.Session, base_url: str, admin: dict[str, str]
) -> Iterator[dict[str, str]]:
    product_data = {
        "nome": f"pytest-product-{uuid4().hex}",
        "preco": 100,
        "descricao": "Produto criado pela suíte pytest",
        "quantidade": 10,
    }
    created = api.post(
        f"{base_url}/produtos",
        headers={"Authorization": admin["token"]},
        json=product_data,
        timeout=REQUEST_TIMEOUT,
    )
    assert created.status_code == 201, created.text
    product_data["_id"] = response_json(created)["_id"]

    try:
        yield product_data
    finally:
        deleted = api.delete(
            f"{base_url}/produtos/{product_data['_id']}",
            headers={"Authorization": admin["token"]},
            timeout=REQUEST_TIMEOUT,
        )
        assert deleted.status_code == 200, deleted.text


@pytest.fixture
def customer(
    api: requests.Session, base_url: str
) -> Iterator[dict[str, str]]:
    user = create_user(api, base_url)
    try:
        user["token"] = login(api, base_url, user)["authorization"]
        yield user
    finally:
        deleted = api.delete(
            f"{base_url}/usuarios/{user['_id']}", timeout=REQUEST_TIMEOUT
        )
        assert deleted.status_code == 200, deleted.text


@pytest.fixture
def cart(
    api: requests.Session,
    base_url: str,
    customer: dict[str, str],
    product: dict[str, str],
) -> Iterator[dict[str, str]]:
    created = api.post(
        f"{base_url}/carrinhos",
        headers={"Authorization": customer["token"]},
        json={
            "produtos": [{"idProduto": product["_id"], "quantidade": 1}]
        },
        timeout=REQUEST_TIMEOUT,
    )
    assert created.status_code == 201, created.text
    cart_data = {"_id": response_json(created)["_id"]}

    try:
        yield cart_data
    finally:
        cancelled = api.delete(
            f"{base_url}/carrinhos/cancelar-compra",
            headers={"Authorization": customer["token"]},
            timeout=REQUEST_TIMEOUT,
        )
        assert cancelled.status_code == 200, cancelled.text


def test_post_login_returns_authorization_token(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    body = login(api, base_url, regular_user)

    assert body["message"] == "Login realizado com sucesso"
    assert body["authorization"]


def test_get_usuarios_lists_registered_user(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    response = api.get(
        f"{base_url}/usuarios",
        params={"_id": regular_user["_id"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["quantidade"] == len(body["usuarios"])
    assert any(user["_id"] == regular_user["_id"] for user in body["usuarios"])


def test_post_usuarios_creates_user(
    api: requests.Session, base_url: str
) -> None:
    user = {
        "nome": "Pytest Created User",
        "email": f"pytest-created-{uuid4().hex}@example.com",
        "password": "pytest-password",
        "administrador": "false",
    }
    response = api.post(
        f"{base_url}/usuarios", json=user, timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == 201, response.text
    body = response_json(response)
    assert body["message"] == "Cadastro realizado com sucesso"
    assert body["_id"]

    deleted = api.delete(
        f"{base_url}/usuarios/{body['_id']}", timeout=REQUEST_TIMEOUT
    )
    assert deleted.status_code == 200, deleted.text


def test_get_usuario_by_id_returns_registered_user(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    response = api.get(
        f"{base_url}/usuarios/{regular_user['_id']}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["_id"] == regular_user["_id"]
    assert body["email"] == regular_user["email"]


def test_put_usuario_by_id_updates_registered_user(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    updated_name = "Pytest User Updated"
    response = api.put(
        f"{base_url}/usuarios/{regular_user['_id']}",
        json={
            "nome": updated_name,
            "email": regular_user["email"],
            "password": regular_user["password"],
            "administrador": regular_user["administrador"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert response_json(response)["message"] == "Registro alterado com sucesso"

    details = api.get(
        f"{base_url}/usuarios/{regular_user['_id']}", timeout=REQUEST_TIMEOUT
    )
    assert details.status_code == 200, details.text
    assert response_json(details)["nome"] == updated_name


def test_delete_usuario_by_id_removes_registered_user(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    response = api.delete(
        f"{base_url}/usuarios/{regular_user['_id']}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200, response.text
    assert "excluído com sucesso" in response_json(response)["message"]


def test_get_produtos_lists_registered_products(
    api: requests.Session, base_url: str, product: dict[str, str]
) -> None:
    response = api.get(
        f"{base_url}/produtos",
        params={"_id": product["_id"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["quantidade"] == len(body["produtos"])
    assert any(item["_id"] == product["_id"] for item in body["produtos"])


def test_post_produtos_creates_product(
    api: requests.Session, base_url: str, admin: dict[str, str]
) -> None:
    product_data = {
        "nome": f"pytest-created-product-{uuid4().hex}",
        "preco": 200,
        "descricao": "Produto de teste",
        "quantidade": 5,
    }
    response = api.post(
        f"{base_url}/produtos",
        headers={"Authorization": admin["token"]},
        json=product_data,
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 201, response.text
    body = response_json(response)
    assert body["message"] == "Cadastro realizado com sucesso"
    assert body["_id"]

    deleted = api.delete(
        f"{base_url}/produtos/{body['_id']}",
        headers={"Authorization": admin["token"]},
        timeout=REQUEST_TIMEOUT,
    )
    assert deleted.status_code == 200, deleted.text


def test_get_produto_by_id_returns_registered_product(
    api: requests.Session, base_url: str, product: dict[str, str]
) -> None:
    response = api.get(
        f"{base_url}/produtos/{product['_id']}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["_id"] == product["_id"]
    assert body["nome"] == product["nome"]


def test_put_produto_by_id_updates_registered_product(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
) -> None:
    updated_name = f"{product['nome']}-updated"
    response = api.put(
        f"{base_url}/produtos/{product['_id']}",
        headers={"Authorization": admin["token"]},
        json={
            "nome": updated_name,
            "preco": 125,
            "descricao": product["descricao"],
            "quantidade": product["quantidade"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert response_json(response)["message"] == "Registro alterado com sucesso"

    details = api.get(
        f"{base_url}/produtos/{product['_id']}", timeout=REQUEST_TIMEOUT
    )
    assert details.status_code == 200, details.text
    assert response_json(details)["nome"] == updated_name


def test_delete_produto_by_id_removes_registered_product(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
) -> None:
    response = api.delete(
        f"{base_url}/produtos/{product['_id']}",
        headers={"Authorization": admin["token"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert "excluído com sucesso" in response_json(response)["message"]


def test_get_carrinhos_lists_registered_cart(
    api: requests.Session, base_url: str, cart: dict[str, str]
) -> None:
    response = api.get(f"{base_url}/carrinhos", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["quantidade"] == len(body["carrinhos"])
    assert any(item["_id"] == cart["_id"] for item in body["carrinhos"])


def test_post_carrinhos_creates_cart(
    api: requests.Session,
    base_url: str,
    customer: dict[str, str],
    product: dict[str, str],
) -> None:
    response = api.post(
        f"{base_url}/carrinhos",
        headers={"Authorization": customer["token"]},
        json={
            "produtos": [{"idProduto": product["_id"], "quantidade": 1}]
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 201, response.text
    body = response_json(response)
    assert body["message"] == "Cadastro realizado com sucesso"
    assert body["_id"]

    cancelled = api.delete(
        f"{base_url}/carrinhos/cancelar-compra",
        headers={"Authorization": customer["token"]},
        timeout=REQUEST_TIMEOUT,
    )
    assert cancelled.status_code == 200, cancelled.text


def test_get_carrinho_by_id_returns_registered_cart(
    api: requests.Session,
    base_url: str,
    cart: dict[str, str],
    customer: dict[str, str],
    product: dict[str, str],
) -> None:
    response = api.get(
        f"{base_url}/carrinhos/{cart['_id']}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert body["_id"] == cart["_id"]
    assert body["idUsuario"] == customer["_id"]
    assert body["produtos"][0]["idProduto"] == product["_id"]


def test_delete_carrinhos_concluir_compra_completes_purchase(
    api: requests.Session,
    base_url: str,
    cart: dict[str, str],
    customer: dict[str, str],
) -> None:
    response = api.delete(
        f"{base_url}/carrinhos/concluir-compra",
        headers={"Authorization": customer["token"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert "excluído com sucesso" in response_json(response)["message"]


def test_delete_carrinhos_cancelar_compra_cancels_purchase(
    api: requests.Session,
    base_url: str,
    cart: dict[str, str],
    customer: dict[str, str],
) -> None:
    response = api.delete(
        f"{base_url}/carrinhos/cancelar-compra",
        headers={"Authorization": customer["token"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert "excluído com sucesso" in response_json(response)["message"]
