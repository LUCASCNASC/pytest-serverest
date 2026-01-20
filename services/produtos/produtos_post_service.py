import requests
import uuid
from utils.config import BASE_URL, NOME, PRECO, DESCRICAO, QUANTIDADE
from services.login.login_post_service import login

def produtos():
    token = login().json()["authorization"]

    payload = {
        "nome": f"{NOME}-{uuid.uuid4()}",
        "preco": int(PRECO),
        "descricao": DESCRICAO,
        "quantidade": int(QUANTIDADE)
    }

    headers = {
        "Authorization": token
    }

    response = requests.post(
        f"{BASE_URL}/produtos",
        json=payload,
        headers=headers
    )

    return response