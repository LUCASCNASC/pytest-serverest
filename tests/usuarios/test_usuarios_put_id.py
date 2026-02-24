import pytest
import requests
from faker import Faker

# Endpoint: PUT /usuarios/{id}

fake = Faker()

class TestUpdateUserById:
    
    # Esta fixture resolve o problema da injeção da URL no nível da classe.
    # Ela roda uma vez para a classe e atribui a string final vinda do conftest.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        TestUpdateUserById.url_base = f"{base_url}/usuarios"

    def test_put_change_user_with_success_200(self):
        """Cenário 200: Registro alterado com sucesso"""
        # Cria um usuário para garantir que o ID existe
        payload_create = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        res_post = requests.post(self.url_base, json=payload_create)
        user_id = res_post.json()["_id"]

        # Dados para alteração
        payload_update = {
            "nome": "Lucas Editado",
            "email": fake.email(),
            "password": "nova_senha_123",
            "administrador": "true"
        }

        response = requests.put(f"{self.url_base}/{user_id}", json=payload_update)

        assert response.status_code == 200
        assert response.json()["message"] == "Registro alterado com sucesso"

    def test_put_register_new_user_201(self):
        """Cenário 201: Cadastro realizado com sucesso (ID não encontrado)"""
        # Geramos um ID aleatório que não existe no sistema
        id_inexistente = f"novo_{fake.uuid4()[:8]}"
        
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }

        response = requests.put(f"{self.url_base}/{id_inexistente}", json=payload)

        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_put_email_duplicate_400(self):
        """Cenário 400: Este email já está sendo usado"""
        # Garante um usuário 'A' no sistema
        email_em_uso = fake.email()
        requests.post(self.url_base, json={
            "nome": "Usuario A", "email": email_em_uso, "password": "123", "administrador": "true"
        })

        # Garante um usuário 'B' que tentaremos editar
        res_b = requests.post(self.url_base, json={
            "nome": "Usuario B", "email": fake.email(), "password": "123", "administrador": "true"
        })
        id_b = res_b.json()["_id"]

        # Tenta dar um PUT no usuário 'B' usando o email do usuário 'A'
        payload_conflito = {
            "nome": "Lucas Conflito",
            "email": email_em_uso,
            "password": "teste",
            "administrador": "true"
        }

        response = requests.put(f"{self.url_base}/{id_b}", json=payload_conflito)

        assert response.status_code == 400
        assert response.json()["message"] == "Este email já está sendo usado"