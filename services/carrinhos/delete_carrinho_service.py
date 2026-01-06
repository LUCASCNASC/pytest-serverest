import requests
from utils.config import BASE_URL
from services.login.login_post_service import login

def deletar_carrinho():
    token = login().json()["authorization"]

    headers = {
        "Authorization": token
    }

    response = requests.delete(
        f"{BASE_URL}/carrinhos/cancelar-compra",
        headers=headers
    )

    return response
