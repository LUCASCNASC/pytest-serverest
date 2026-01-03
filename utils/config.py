import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
NOME = os.getenv("NOME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
ADMINISTRADOR = os.getenv("ADMINISTRADOR")
