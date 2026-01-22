import requests
from utils.config import BASE_URL

def get_produtos(params=None):
    response = requests.get(
        f"{BASE_URL}/produtos",
        params=params
    )
    return response
