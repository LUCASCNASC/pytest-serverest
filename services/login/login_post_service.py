import requests
from utils.config import BASE_URL, EMAIL, PASSWORD

def login(email=EMAIL, password=PASSWORD):
    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(
        f"{BASE_URL}/login",
        json=payload
    )

    return response