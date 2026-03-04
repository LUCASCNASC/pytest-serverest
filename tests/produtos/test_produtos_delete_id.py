import pytest;
import requests;
from faker import Faker;

# Endpoint: DELETE /produtos/{id}

fake = Faker()

class TestDeleteProductById:
    
    # Fixture que configura as URLs da classe usando a base_url do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        TestDeleteProductById.url_base = f"{base_url}/produtos"
        TestDeleteProductById.url_carrinhos = f"{base_url}/carrinhos"

    def test_delete_product_with_sucess_200(self, auth_token):
        """Cenário 200: Registro excluído com sucesso"""
        # Preparação: Criar um produto para garantir um ID válido
        headers = {'Authorization': auth_token}
        payload = {
            "nome": f"Produto para Deletar {fake.random_number()}",
            "preco": 10,
            "descricao": "Teste Delete",
            "quantidade": 1
        }
        res_post = requests.post(self.url_base, headers=headers, json=payload)
        produto_id = res_post.json()["_id"]

        # Execução: Excluir o produto usando self.url_base
        response = requests.delete(f"{self.url_base}/{produto_id}", headers=headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Registro excluído com sucesso"

    def test_delete_product_linked_to_cart_400(self, auth_token, produto_id):
        """Cenário 400: Não é permitido excluir produto que faz parte de carrinho"""
        headers = {'Authorization': auth_token}
        
        # Preparação: Colocar o produto em um carrinho (usando a URL da classe)
        payload_carrinho = {
            "produtos": [{"idProduto": produto_id, "quantidade": 1}]
        }
        requests.post(self.url_carrinhos, headers=headers, json=payload_carrinho)

        # Execução: Tentar excluir o produto que está no carrinho
        response = requests.delete(f"{self.url_base}/{produto_id}", headers=headers)

        assert response.status_code == 400
        assert response.json()["message"] == "Não é permitido excluir produto que faz parte de carrinho"

    def test_delete_product_without_token_401(self):
        """Cenário 401: Token ausente ou inválido"""
        # Execução sem header de autorização
        response = requests.delete(f"{self.url_base}/id_qualquer")
        
        assert response.status_code == 401
        assert "Token de acesso ausente" in response.json()["message"]

    def test_delete_product_without_permission_admin_403(self, base_url):
        """Cenário 403: Rota exclusiva para administradores"""
        # 1. Criar e logar com usuário comum (admin: false)
        email_comum = fake.email()
        url_usuarios = f"{base_url}/usuarios"
        url_login = f"{base_url}/login"
        
        requests.post(url_usuarios, json={
            "nome": "Common User", "email": email_comum, "password": "123", "administrador": "false"
        })
        login_res = requests.post(url_login, json={"email": email_comum, "password": "123"})
        token_comum = login_res.json()["authorization"]
        
        # 2. Tentativa de exclusão sem permissão
        headers = {'Authorization': token_comum}
        response = requests.delete(f"{self.url_base}/id_qualquer", headers=headers)
        
        assert response.status_code == 403
        assert response.json()["message"] == "Rota exclusiva para administradores"
        