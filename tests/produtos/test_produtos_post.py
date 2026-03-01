import pytest
import requests
from faker import Faker

# Endpoint: POST /produtos

fake = Faker()

class TestRegisterProduct:
    
    # Esta fixture resolve o problema da URL na classe, injetando a string do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribui o valor da string de URL ao atributo da classe
        TestRegisterProduct.url = f"{base_url}/produtos"

    def test_register_product_with_sucess_201(self, auth_token):
        """Cenário 201: Cadastro com sucesso (Exige Token Admin)"""
        headers = {'Authorization': auth_token}
        payload = {
            "nome": f"Produto {fake.word()} {fake.random_number()}",
            "preco": 470,
            "descricao": "Mouse",
            "quantidade": 381
        }
        # Usa self.url definido no setup da classe
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_register_product_name_duplicate_400(self, auth_token):
        """Cenário 400: Já existe produto com esse nome"""
        headers = {'Authorization': auth_token}
        nome_fixo = f"Produto Repetido {fake.random_number()}"
        payload = {"nome": nome_fixo, "preco": 10, "descricao": "Teste", "quantidade": 5}
        
        # Primeira criação
        requests.post(self.url, headers=headers, json=payload)
        
        # Segunda tentativa com o mesmo nome
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 400
        assert response.json()["message"] == "Já existe produto com esse nome"

    def test_register_product_without_token_401(self):
        """Cenário 401: Token ausente, inválido ou expirado"""
        # Requisição enviada sem o header Authorization usando self.url
        response = requests.post(self.url, json={})
        
        assert response.status_code == 401
        assert "Token de acesso ausente" in response.json()["message"]

    def test_register_product_without_permission_admin_403(self, base_url):
        """Cenário 403: Rota exclusiva para administradores"""
        # 1. Criar e logar com um usuário comum (administrador: false)
        email_comum = fake.email()
        url_usuarios = f"{base_url}/usuarios"
        url_login = f"{base_url}/login"

        requests.post(url_usuarios, json={
            "nome": "User Comum", "email": email_comum, "password": "123", "administrador": "false"
        })
        login_res = requests.post(url_login, 
                                  json={"email": email_comum, "password": "123"})
        token_comum = login_res.json()["authorization"]
        
        # 2. Tentar cadastrar produto com token sem permissão
        headers = {'Authorization': token_comum}
        response = requests.post(self.url, headers=headers, json={})
        
        assert response.status_code == 403
        assert response.json()["message"] == "Rota exclusiva para administradores"
        