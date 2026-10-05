from uuid import uuid4

import pytest
import requests


REQUEST_TIMEOUT = 10


def response_json(response: requests.Response) -> dict:
    assert response.headers.get("Content-Type", "").startswith("application/json")
    return response.json()


@pytest.mark.parametrize(
    ("path", "collection_key"),
    [
        ("/usuarios", "usuarios"),
        ("/produtos", "produtos"),
        ("/carrinhos", "carrinhos"),
    ],
)
def test_list_resources_returns_consistent_collection(
    api: requests.Session,
    base_url: str,
    path: str,
    collection_key: str,
) -> None:
    response = api.get(f"{base_url}{path}", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200, response.text
    body = response_json(response)
    assert isinstance(body[collection_key], list)
    assert body["quantidade"] == len(body[collection_key])


def test_login_rejects_invalid_credentials(
    api: requests.Session, base_url: str
) -> None:
    response = api.post(
        f"{base_url}/login",
        json={
            "email": f"pytest-{uuid4().hex}@example.com",
            "password": "invalid-password",
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 401
    assert "message" in response_json(response)


@pytest.fixture
def admin(api: requests.Session, base_url: str) -> dict[str, str]:
    email = f"pytest-admin-{uuid4().hex}@example.com"
    created = api.post(
        f"{base_url}/usuarios",
        json={
            "nome": "Pytest Admin",
            "email": email,
            "password": "pytest-password",
            "administrador": "true",
        },
        timeout=REQUEST_TIMEOUT,
    )
    assert created.status_code == 201, created.text
    user_id = response_json(created)["_id"]

    try:
        login = api.post(
            f"{base_url}/login",
            json={"email": email, "password": "pytest-password"},
            timeout=REQUEST_TIMEOUT,
        )
        assert login.status_code == 200, login.text
        token = response_json(login)["authorization"]
        yield {"id": user_id, "token": token}
    finally:
        deleted = api.delete(
            f"{base_url}/usuarios/{user_id}", timeout=REQUEST_TIMEOUT
        )
        assert deleted.status_code == 200, deleted.text


@pytest.fixture
def product(
    api: requests.Session, base_url: str, admin: dict[str, str]
) -> dict[str, str]:
    name = f"pytest-product-{uuid4().hex}"
    response = api.post(
        f"{base_url}/produtos",
        headers={"Authorization": admin["token"]},
        json={
            "nome": name,
            "preco": 100,
            "descricao": "Produto criado pela suíte pytest",
            "quantidade": 10,
        },
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code == 201, response.text
    product_id = response_json(response)["_id"]

    try:
        yield {"id": product_id, "name": name}
    finally:
        deleted = api.delete(
            f"{base_url}/produtos/{product_id}",
            headers={"Authorization": admin["token"]},
            timeout=REQUEST_TIMEOUT,
        )
        assert deleted.status_code == 200, deleted.text


def test_admin_can_create_read_update_and_delete_product(
    api: requests.Session, base_url: str, admin: dict[str, str], product: dict[str, str]
) -> None:
    headers = {"Authorization": admin["token"]}
    details = api.get(
        f"{base_url}/produtos/{product['id']}", timeout=REQUEST_TIMEOUT
    )
    assert details.status_code == 200, details.text
    assert response_json(details)["nome"] == product["name"]

    updated_name = f"{product['name']}-updated"
    updated = api.put(
        f"{base_url}/produtos/{product['id']}",
        headers=headers,
        json={
            "nome": updated_name,
            "preco": 125,
            "descricao": "Produto atualizado pela suíte pytest",
            "quantidade": 8,
        },
        timeout=REQUEST_TIMEOUT,
    )
    assert updated.status_code == 200, updated.text
    assert response_json(updated)["message"] == "Registro alterado com sucesso"

    verified = api.get(
        f"{base_url}/produtos/{product['id']}", timeout=REQUEST_TIMEOUT
    )
    assert verified.status_code == 200, verified.text
    assert response_json(verified)["nome"] == updated_name

    deleted = api.delete(
        f"{base_url}/produtos/{product['id']}",
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    assert deleted.status_code == 200, deleted.text
    assert "excluído com sucesso" in response_json(deleted)["message"]

    missing = api.get(
        f"{base_url}/produtos/{product['id']}", timeout=REQUEST_TIMEOUT
    )
    assert missing.status_code == 400, missing.text


def test_user_can_create_and_cancel_cart(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
) -> None:
    email = f"pytest-customer-{uuid4().hex}@example.com"
    user_response = api.post(
        f"{base_url}/usuarios",
        json={
            "nome": "Pytest Customer",
            "email": email,
            "password": "pytest-password",
            "administrador": "false",
        },
        timeout=REQUEST_TIMEOUT,
    )
    assert user_response.status_code == 201, user_response.text
    user_id = response_json(user_response)["_id"]
    cart_created = False

    try:
        login = api.post(
            f"{base_url}/login",
            json={"email": email, "password": "pytest-password"},
            timeout=REQUEST_TIMEOUT,
        )
        assert login.status_code == 200, login.text
        token = response_json(login)["authorization"]

        cart = api.post(
            f"{base_url}/carrinhos",
            headers={"Authorization": token},
            json={"produtos": [{"idProduto": product["id"], "quantidade": 1}]},
            timeout=REQUEST_TIMEOUT,
        )
        assert cart.status_code == 201, cart.text
        cart_created = True
        cart_id = response_json(cart)["_id"]

        details = api.get(
            f"{base_url}/carrinhos/{cart_id}", timeout=REQUEST_TIMEOUT
        )
        assert details.status_code == 200, details.text
        cart_body = response_json(details)
        assert cart_body["idUsuario"] == user_id
        assert cart_body["produtos"][0]["idProduto"] == product["id"]

        cancelled = api.delete(
            f"{base_url}/carrinhos/cancelar-compra",
            headers={"Authorization": token},
            timeout=REQUEST_TIMEOUT,
        )
        assert cancelled.status_code == 200, cancelled.text
        cart_created = False
    finally:
        if cart_created:
            api.delete(
                f"{base_url}/carrinhos/cancelar-compra",
                headers={"Authorization": token},
                timeout=REQUEST_TIMEOUT,
            )
        deleted = api.delete(
            f"{base_url}/usuarios/{user_id}", timeout=REQUEST_TIMEOUT
        )
        assert deleted.status_code == 200, deleted.text
