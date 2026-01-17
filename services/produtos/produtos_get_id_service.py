import requests
from utils.config import BASE_URL

def get_id_produtos(id, params=None):
    response = requests.get(
        f"{BASE_URL}/produtos/{id}",
        params=params
    )
    return response
