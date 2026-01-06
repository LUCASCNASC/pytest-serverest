import requests
from utils.config import BASE_URL

def get_usuarios(params=None):
    response = requests.get(
        f"{BASE_URL}/usuarios",
        params=params
    )
    return response
