import requests
from utils.config import BASE_URL

def get_carrinhos_by_id(carrinho_id):
    response = requests.get(
        f"{BASE_URL}/carrinhos/{carrinho_id}"
    )

    return response