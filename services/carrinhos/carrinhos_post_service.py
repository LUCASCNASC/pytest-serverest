import requests
from utils.config import BASE_URL
from services.login.login_post_service import login
from services.produtos.produtos_post_service import produtos
from services.carrinhos.carrinhos_delete_service import deletar_carrinho

def criar_carrinho():
    deletar_carrinho()  # limpa antes

    produto_response = produtos()
    produto_id = produto_response.json()["_id"]

    token = login().json()["authorization"]

    payload = {
        "produtos": [
            {
                "idProduto": produto_id,
                "quantidade": 1
            }
        ]
    }

    headers = {
        "Authorization": token
    }

    return requests.post(
        f"{BASE_URL}/carrinhos",
        json=payload,
        headers=headers
    )
