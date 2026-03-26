import pytest;
import requests;
from faker import Faker;

# Endpoint: Serverest POST /usuarios

fake = Faker();

class TestRegisterUser:
    
    # This fixture solves the URL problem at the class level. 
    # Fetch the base_url of the conftest and assign it to the 'url' attribute of the class.
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
        
        # Now self.url contains the string "https://serverest.dev/usuarios"
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_register_user_email_duplicate_400(self):
        """Valida a tentativa de cadastro com e-mail já existente (Status 400)"""
        # Test data with dynamic email to avoid conflicts, but repeated in the scenario.
        email_repetido = fake.email()
        payload = {
            "nome": "Fulano da silva",
            "email": email_repetido,
            "password": "teste",
            "administrador": "true"
        }
        
        # Ensure the email address already exists in the system before validating the error.
        requests.post(self.url, json=payload)
        
        # Second attempt.
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 400
        assert response.json()["message"] == "Este email já está sendo usado"
        