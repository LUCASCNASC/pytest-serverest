import pytest
import requests
from faker import Faker

# Endpoint: POST /usuarios

fake = Faker()

class TestRegisterUser:
    
    # Esta fixture resolve o problema da URL no nível da classe. 
    # Ela busca a base_url do conftest e a atribui ao atributo 'url' da classe.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        TestRegisterUser.url = f"{base_url}/usuarios"

    def test_register_user_with_success_201(self):
        """Valida o cadastro de um novo usuário com sucesso (Status 201)"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        
        # Agora self.url contém a string correta (ex: https://serverest.dev/usuarios)
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_register_user_email_duplicate_400(self):
        """Valida a tentativa de cadastro com e-mail já existente (Status 400)"""
        # Massa de teste com e-mail dinâmico para evitar conflitos, mas repetido no cenário
        email_repetido = fake.email()
        payload = {
            "nome": "Fulano da silva",
            "email": email_repetido,
            "password": "teste",
            "administrador": "true"
        }
        
        # Garante que o e-mail já existe no sistema antes de validar o erro
        requests.post(self.url, json=payload)
        
        # Segunda tentativa
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 400
        assert response.json()["message"] == "Este email já está sendo usado"
        