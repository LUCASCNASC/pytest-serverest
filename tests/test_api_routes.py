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
    assert cart["_id"]
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
    assert cart["_id"]
    response = api.delete(
        f"{base_url}/carrinhos/cancelar-compra",
        headers={"Authorization": customer["token"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200, response.text
    assert "excluído com sucesso" in response_json(response)["message"]


def test_post_login_rejects_unknown_credentials(
    api: requests.Session, base_url: str
) -> None:
    response = api.post(
        f"{base_url}/login",
        json={
            "email": f"pytest-unknown-{uuid4().hex}@example.com",
            "password": "invalid-password",
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 401, response.text
    assert response_json(response)["message"] == "Email e/ou senha inválidos"


def test_post_usuarios_rejects_duplicate_email(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    response = api.post(
        f"{base_url}/usuarios",
        json={
            "nome": "Duplicate User",
            "email": regular_user["email"],
            "password": regular_user["password"],
            "administrador": regular_user["administrador"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == "Este email já está sendo usado"


def test_get_usuario_by_id_returns_400_for_unknown_user(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(
        f"{base_url}/usuarios/{uuid4().hex[:16]}",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == "Usuário não encontrado"


def test_delete_usuario_by_id_rejects_user_with_cart(
    api: requests.Session,
    base_url: str,
    customer: dict[str, str],
    cart: dict[str, str],
) -> None:
    assert cart["_id"]
    response = api.delete(
        f"{base_url}/usuarios/{customer['_id']}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == (
        "Não é permitido excluir usuário com carrinho cadastrado"
    )


def test_put_usuario_by_id_rejects_duplicate_email(
    api: requests.Session, base_url: str, regular_user: dict[str, str]
) -> None:
    other_user = create_user(api, base_url)
    try:
        response = api.put(
            f"{base_url}/usuarios/{regular_user['_id']}",
            json={
                "nome": regular_user["nome"],
                "email": other_user["email"],
                "password": regular_user["password"],
                "administrador": regular_user["administrador"],
            },
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 400, response.text
        assert response_json(response)["message"] == (
            "Este email já está sendo usado"
        )
    finally:
        deleted = api.delete(
            f"{base_url}/usuarios/{other_user['_id']}",
            timeout=REQUEST_TIMEOUT,
        )
        assert deleted.status_code == 200, deleted.text


def test_get_produto_by_id_returns_400_for_unknown_product(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(
        f"{base_url}/produtos/{uuid4().hex[:16]}",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == "Produto não encontrado"


def test_post_produtos_rejects_duplicate_name(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
) -> None:
    response = api.post(
        f"{base_url}/produtos",
        headers={"Authorization": admin["token"]},
        json={
            "nome": product["nome"],
            "preco": product["preco"],
            "descricao": product["descricao"],
            "quantidade": product["quantidade"],
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == "Já existe produto com esse nome"


@pytest.mark.parametrize(
    ("method", "path", "operation"),
    [
        ("POST", "/produtos", "create"),
        ("PUT", "/produtos/{product_id}", "update"),
        ("DELETE", "/produtos/{product_id}", "delete"),
    ],
)
@pytest.mark.parametrize(
    ("authorization", "expected_status"),
    [("missing", 401), ("customer", 403)],
    ids=["missing-token", "non-admin"],
)
def test_admin_product_routes_reject_unauthorized_access(
    api: requests.Session,
    base_url: str,
    product: dict[str, str],
    customer: dict[str, str],
    method: str,
    path: str,
    operation: str,
    authorization: str,
    expected_status: int,
) -> None:
    request_path = path.format(product_id=product["_id"])
    headers = (
        {"Authorization": customer["token"]}
        if authorization == "customer"
        else {}
    )
    kwargs: dict[str, object] = {
        "headers": headers,
        "timeout": REQUEST_TIMEOUT,
    }
    if operation in {"create", "update"}:
        kwargs["json"] = {
            "nome": product["nome"],
            "preco": product["preco"],
            "descricao": product["descricao"],
            "quantidade": product["quantidade"],
        }

    response = api.request(
        method, f"{base_url}{request_path}", **kwargs
    )

    assert response.status_code == expected_status, response.text
    expected_message = (
        "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"
        if expected_status == 401
        else "Rota exclusiva para administradores"
    )
    assert response_json(response)["message"] == expected_message


def test_delete_produto_by_id_rejects_product_in_cart(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
    cart: dict[str, str],
) -> None:
    assert cart["_id"]
    response = api.delete(
        f"{base_url}/produtos/{product['_id']}",
        headers={"Authorization": admin["token"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == (
        "Não é permitido excluir produto que faz parte de carrinho"
    )


def test_put_produto_by_id_rejects_duplicate_name(
    api: requests.Session,
    base_url: str,
    admin: dict[str, str],
    product: dict[str, str],
) -> None:
    duplicate = {
        "nome": f"pytest-duplicate-product-{uuid4().hex}",
        "preco": 150,
        "descricao": "Produto duplicado",
        "quantidade": 5,
    }
    created = api.post(
        f"{base_url}/produtos",
        headers={"Authorization": admin["token"]},
        json=duplicate,
        timeout=REQUEST_TIMEOUT,
    )
    assert created.status_code == 201, created.text
    duplicate_id = response_json(created)["_id"]

    try:
        response = api.put(
            f"{base_url}/produtos/{product['_id']}",
            headers={"Authorization": admin["token"]},
            json={
                **duplicate,
                "nome": duplicate["nome"],
            },
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 400, response.text
        assert response_json(response)["message"] == (
            "Já existe produto com esse nome"
        )
    finally:
        deleted = api.delete(
            f"{base_url}/produtos/{duplicate_id}",
            headers={"Authorization": admin["token"]},
            timeout=REQUEST_TIMEOUT,
        )
        assert deleted.status_code == 200, deleted.text


@pytest.mark.parametrize(
    ("scenario", "products", "expected_message"),
    [
        (
            "unknown-product",
            [{"idProduto": "USE_MISSING_PRODUCT_ID", "quantidade": 1}],
            "Produto não encontrado",
        ),
        (
            "duplicate-product-in-request",
            [
                {"idProduto": "use-fixture-product", "quantidade": 1},
                {"idProduto": "use-fixture-product", "quantidade": 1},
            ],
            "Não é permitido possuir produto duplicado",
        ),
        (
            "insufficient-stock",
            [{"idProduto": "use-fixture-product", "quantidade": 11}],
            "Produto não possui quantidade suficiente",
        ),
    ],
)
def test_post_carrinhos_rejects_invalid_products(
    api: requests.Session,
    base_url: str,
    customer: dict[str, str],
    product: dict[str, str],
    scenario: str,
    products: list[dict[str, object]],
    expected_message: str,
) -> None:
    request_products = [
        {
            **item,
            "idProduto": (
                product["_id"]
                if item["idProduto"] == "use-fixture-product"
                else f"pytest-missing-{uuid4().hex}"
            ),
        }
        for item in products
    ]
    response = api.post(
        f"{base_url}/carrinhos",
        headers={"Authorization": customer["token"]},
        json={"produtos": request_products},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, f"{scenario}: {response.text}"
    assert response_json(response)["message"] == expected_message


def test_post_carrinhos_rejects_second_cart_for_user(
    api: requests.Session,
    base_url: str,
    customer: dict[str, str],
    product: dict[str, str],
    cart: dict[str, str],
) -> None:
    assert cart["_id"]
    response = api.post(
        f"{base_url}/carrinhos",
        headers={"Authorization": customer["token"]},
        json={
            "produtos": [{"idProduto": product["_id"], "quantidade": 1}]
        },
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == (
        "Não é permitido ter mais de 1 carrinho"
    )


def test_post_carrinhos_requires_authorization(
    api: requests.Session, base_url: str, product: dict[str, str]
) -> None:
    response = api.post(
        f"{base_url}/carrinhos",
        json={"produtos": [{"idProduto": product["_id"], "quantidade": 1}]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 401, response.text
    assert response_json(response)["message"] == (
        "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"
    )


def test_get_carrinho_by_id_returns_400_for_unknown_cart(
    api: requests.Session, base_url: str
) -> None:
    response = api.get(
        f"{base_url}/carrinhos/{uuid4().hex[:16]}",
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400, response.text
    assert response_json(response)["message"] == "Carrinho não encontrado"


@pytest.mark.parametrize(
    ("path", "operation"),
    [
        ("/carrinhos/concluir-compra", "conclude"),
        ("/carrinhos/cancelar-compra", "cancel"),
    ],
)
def test_delete_cart_actions_require_authorization(
    api: requests.Session,
    base_url: str,
    path: str,
    operation: str,
) -> None:
    response = api.delete(
        f"{base_url}{path}", timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 401, f"{operation}: {response.text}"
    assert response_json(response)["message"] == (
        "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"
    )
