import requests
from faker import Faker

fake = Faker()

class TestPostProdutos:
    url = "https://serverest.dev/produtos"

    def test_cadastrar_produto_sucesso_201(self, auth_token):
        """Cenário 201: Cadastro com sucesso"""
        headers = {'Authorization': auth_token}
        payload = {
            "nome": f"Produto {fake.word()} {fake.random_number()}",
            "preco": 470,
            "descricao": "Mouse",
            "quantidade": 381
        }
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_cadastrar_produto_nome_duplicado_400(self, auth_token):
        """Cenário 400: Já existe produto com esse nome"""
        headers = {'Authorization': auth_token}
        nome_fixo = f"Produto Fixo {fake.random_number()}"
        payload = {"nome": nome_fixo, "preco": 100, "descricao": "Desc", "quantidade": 10}
        
        # Garante a primeira criação
        requests.post(self.url, headers=headers, json=payload)
        
        # Tenta criar novamente com o mesmo nome
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 400
        assert response.json()["message"] == "Já existe produto com esse nome"

    def test_cadastrar_produto_sem_token_401(self):
        """Cenário 401: Token ausente, inválido ou expirado"""
        # Enviamos a requisição sem o header de Authorization
        response = requests.post(self.url, json={})
        
        assert response.status_code == 401
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"

    def test_cadastrar_produto_usuario_comum_403(self):
        """Cenário 403: Rota exclusiva para administradores"""
        # 1. Cria um usuário comum (administrador: false) e loga com ele
        user_comum = {"nome": "Comum", "email": fake.email(), "password": "123", "administrador": "false"}
        requests.post("https://serverest.dev/usuarios", json=user_comum)
        
        login_res = requests.post("https://serverest.dev/login", 
                                  json={"email": user_comum["email"], "password": "123"})
        token_comum = login_res.json()["authorization"]
        
        # 2. Tenta cadastrar produto com o token de usuário comum
        headers = {'Authorization': token_comum}
        response = requests.post(self.url, headers=headers, json={})
        
        assert response.status_code == 403
        assert response.json()["message"] == "Rota exclusiva para administradores"