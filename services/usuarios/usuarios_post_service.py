import requests
import uuid
from utils.config import BASE_URL, NOME, EMAIL, PASSWORD, ADMINISTRADOR

def usuarios(nome=NOME, email=EMAIL, password=PASSWORD, administrador=ADMINISTRADOR):

    email_dinamico = f"usuario_{uuid.uuid4()}@qa.com"

    payload = {
        "nome": nome,
        "email": email_dinamico,
        "password": password,
        "administrador": administrador
    }

    response = requests.post(
        f"{BASE_URL}/usuarios",
        json=payload
    )

    return response
