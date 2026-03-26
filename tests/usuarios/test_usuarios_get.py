import pytest;
import requests;
from faker import Faker;

# Endpoint: Serverest GET /usuarios

fake = Faker();

class TestSearchUsers:
    
    # This fixture ensures that the URL is correctly constructed using the base_url from conftest.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute
        TestSearchUsers.url = f"{base_url}/usuarios"

    def test_register_user_with_success_201(self):
        """Valida POST /usuarios - Cenário de Sucesso (201)"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        
        # Now self.url contains the string "https://serverest.dev/usuarios"
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_list_users_registered_200(self):
        """Valida GET /usuarios - Cenário de Sucesso (200)"""
        response = requests.get(self.url)
        
        assert response.status_code == 200
        assert "quantidade" in response.json()
        assert "usuarios" in response.json()
        assert isinstance(response.json()["usuarios"], list)
        