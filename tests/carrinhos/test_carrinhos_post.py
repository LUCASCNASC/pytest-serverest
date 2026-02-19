import requests;

# Endpoint: POST /carrinhos

class TestPostCarrinhos:
    url = "https://serverest.dev/carrinhos";

    def test_register_cart_sucess_201(self, auth_token, produto_id):
        """Cenário 201: Cadastro com sucesso""";
        headers = {'Authorization': auth_token};
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        response = requests.post(self.url, headers=headers, json=payload);
        
        assert response.status_code == 201;
        assert response.json()["message"] == "Cadastro realizado com sucesso";
        assert "_id" in response.json();

    def test_register_cart_duplicate_400(self, auth_token, produto_id):
        """Cenário 400: Não é permitido ter mais de 1 carrinho por usuário""";
        headers = {'Authorization': auth_token};
        payload = {"produtos": [{"idProduto": produto_id, "quantidade": 1}]};
        
        # Garante que já existe um carrinho para este usuário
        requests.post(self.url, headers=headers, json=payload);
        
        # Tenta cadastrar o segundo
        response = requests.post(self.url, headers=headers, json=payload);
        
        assert response.status_code == 400;
        assert "Não é permitido ter mais de 1 carrinho" in response.json()["message"];

    def test_register_cart_token_absent_401(self):
        """Cenário 401: Token ausente, inválido ou expirado""";
        payload = {"produtos": [{"idProduto": "id_qualquer", "quantidade": 1}]};
        
        # Requisição sem headers de autorização
        response = requests.post(self.url, json=payload);
        
        assert response.status_code == 401;
        assert "Token de acesso ausente" in response.json()["message"];