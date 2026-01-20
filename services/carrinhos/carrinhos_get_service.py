import requests
from utils.config import BASE_URL

def get_carrinhos(params=None):
    response = requests.get(
        f"{BASE_URL}/carrinhos",
        params=params
    )
    return response