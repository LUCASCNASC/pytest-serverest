import pytest;
import requests;
from faker import Faker;

fake = Faker();

# Endpoint: Serverest GET /usuarios/{id}

class TestSearchUserById:
    
    # This fixture solves the URL problem. It runs once for the class.
    # and inject the correct string from conftest.py
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute
        TestSearchUserById.url_base = f"{base_url}/usuarios"

    def test_search_user_by_id_with_success_200(self):
        """Valida a busca de um usuário por um ID válido (Status 200)"""
        # Primeiro, cadastramos um usuário para garantir que o ID existe
        payload_cadastro = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        cadastro_res = requests.post(self.url_base, json=payload_cadastro)
        user_id = cadastro_res.json()["_id"]

        # Now, we are looking for that specific ID.
        response = requests.get(f"{self.url_base}/{user_id}")
        
        assert response.status_code == 200
        assert response.json()["nome"] == payload_cadastro["nome"]
        assert response.json()["_id"] == user_id
        assert "email" in response.json()

    def test_search_user_by_id_inexistent_400(self):
        """Valida a busca por um ID que não consta no sistema (Status 400)"""
        # Using an ID with a valid format (16 characters), but which does not exist.
        id_inexistente = "nonExistent12345"

        response = requests.get(f"{self.url_base}/{id_inexistente}")

        # If there is a rate limit error (429), the print below will help with debugging
        if response.status_code != 400:
            print(f"\nDebug - Status: {response.status_code}")
            print(f"Debug - Body: {response.json()}")

        assert response.status_code == 400
        assert response.json()["message"] == "Usuário não encontrado"
        