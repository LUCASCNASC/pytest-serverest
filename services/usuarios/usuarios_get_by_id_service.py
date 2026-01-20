import requests
from utils.config import BASE_URL

def get_usuario_by_id(usuario_id):
    response = requests.get(
        f"{BASE_URL}/usuarios/{usuario_id}"
    )

    return response