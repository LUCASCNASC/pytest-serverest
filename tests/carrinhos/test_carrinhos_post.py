import pytest
import requests

# Endpoint: POST /carrinhos

class TestRegisterCart:
    
    # Esta fixture resolve o problema da URL na classe, injetando a string do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribui o valor da string de URL ao atributo da classe
        TestRegisterCart.url = f"{base_url}/carrinhos"

    def test_register_cart_sucess_201(self, auth_token, produto_id):
        """Cenário 201: Cadastro com sucesso"""
        headers = {'Authorization': auth_token}
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        }
        # Usa self.url definido no setup da classe
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 201
        assert response.json()["message"] == "Cadastro realizado com sucesso"
        assert "_id" in response.json()

    def test_register_cart_duplicate_400(self, auth_token, produto_id):
        """Cenário 400: Não é permitido ter mais de 1 carrinho por usuário"""
        headers = {'Authorization': auth_token}
        payload = {"produtos": [{"idProduto": produto_id, "quantidade": 1}]}
        
        # Garante que já existe um carrinho para este usuário
        requests.post(self.url, headers=headers, json=payload)
        
        # Tenta cadastrar o segundo carrinho para o mesmo usuário
        response = requests.post(self.url, headers=headers, json=payload)
        
        assert response.status_code == 400
        assert "Não é permitido ter mais de 1 carrinho" in response.json()["message"]

    def test_register_cart_token_absent_401(self):
        """Cenário 401: Token ausente, inválido ou expirado"""
        payload = {"produtos": [{"idProduto": "id_qualquer", "quantidade": 1}]}
        
        # Requisição sem headers de autorização usando self.url
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 401
        assert "Token de acesso ausente" in response.json()["message"]