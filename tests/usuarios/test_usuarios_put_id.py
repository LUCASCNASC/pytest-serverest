import requests
from faker import Faker

fake = Faker()

class TestPutUsuarios:
    url_base = "https://serverest.dev/usuarios"

    def test_put_alterar_usuario_com_sucesso_200(self):
        """Cenário 200: Registro alterado com sucesso"""
        # 1. Cria um usuário para garantir que o ID existe
        payload_create = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        user_id = requests.post(self.url_base, json=payload_create).json()["_id"]

        # 2. Dados para alteração
        payload_update = {
            "nome": "Lucas Editado",
            "email": fake.email(),
            "password": "nova_senha_123",
            "administrador": "true"
        }

        response = requests.put(f"{self.url_base}/{user_id}", json=payload_update)

        assert response.status_code == 200
        assert response.json()["message"] == "Registro alterado com sucesso"

    def test_put_cadastrar_novo_usuario_201(self):
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

    def test_put_email_duplicado_400(self):
        """Cenário 400: Este email já está sendo usado"""
        # 1. Garante um usuário 'A' no sistema
        email_em_uso = fake.email()
        requests.post(self.url_base, json={
            "nome": "Usuario A", "email": email_em_uso, "password": "123", "administrador": "true"
        })

        # 2. Garante um usuário 'B' que tentaremos editar
        res_b = requests.post(self.url_base, json={
            "nome": "Usuario B", "email": fake.email(), "password": "123", "administrador": "true"
        })
        id_b = res_b.json()["_id"]

        # 3. Tenta dar um PUT no usuário 'B' usando o email do usuário 'A'
        payload_conflito = {
            "nome": "Lucas Conflito",
            "email": email_em_uso,
            "password": "teste",
            "administrador": "true"
        }

        response = requests.put(f"{self.url_base}/{id_b}", json=payload_conflito)

        assert response.status_code == 400
        assert response.json()["message"] == "Este email já está sendo usado"