import requests
from utils.config import BASE_URL


def deletar_usuario(user_id):
    return requests.delete(f"{BASE_URL}/usuarios/{user_id}")
