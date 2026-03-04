import pytest;
import requests;
from faker import Faker;

# Endpoint: GET /usuarios

fake = Faker();

class TestSearchUsers:
    
    # Esta fixture garante que a URL seja montada corretamente usando a base_url do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribuímos o valor correto à variável de classe
        TestSearchUsers.url = f"{base_url}/usuarios"

    def test_register_user_with_success_201(self):
        """Valida POST /usuarios - Cenário de Sucesso (201)"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        
        # Agora self.url contém a string "https://serverest.dev/usuarios"
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
        