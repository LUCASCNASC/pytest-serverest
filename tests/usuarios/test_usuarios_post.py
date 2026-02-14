import requests
from faker import Faker

fake = Faker()

class TestPostUsuarios:
    url = "https://serverest.dev/usuarios"

    def test_cadastrar_usuario_com_sucesso_201(self):
        """Valida o cadastro de um novo usuário com sucesso (Status 201)"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_cadastrar_usuario_email_duplicado_400(self):
        """Valida a tentativa de cadastro com e-mail já existente (Status 400)"""
        # Massa de teste com e-mail fixo
        email_repetido = "beltrano@qa.com.br"
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