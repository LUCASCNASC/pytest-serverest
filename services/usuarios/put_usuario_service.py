import requests
from utils.config import BASE_URL

def put_usuario(user_id, payload):
    response = requests.put(
        f"{BASE_URL}/usuarios/{user_id}",
        json=payload
    )

    return response
