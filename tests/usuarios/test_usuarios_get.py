import requests
from faker import Faker

fake = Faker()

class TestUsuarios:
    url = "https://serverest.dev/usuarios"

    def test_cadastrar_usuario_com_sucesso_201(self):
        """Valida POST /usuarios - Cenário de Sucesso (201)"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        
        response = requests.post(self.url, json=payload)
        
        # Validações baseadas no seu print do POST
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_listar_usuarios_cadastrados_200(self):
        """Valida GET /usuarios - Cenário de Sucesso (200)"""
        response = requests.get(self.url)
        
        # Validações baseadas no seu print do GET
        assert response.status_code == 200
        assert "quantidade" in response.json()
        assert "usuarios" in response.json()
        # Valida se a lista de usuários não está vazia ou é um tipo lista
        assert isinstance(response.json()["usuarios"], list)