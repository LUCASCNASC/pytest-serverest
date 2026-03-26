import pytest;
import requests;

# Endpoint: Serverest POST /carrinhos

class TestRegisterCart:
    
    # This fixture solves the URL problem in the class by injecting the conftest string.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute.
        TestRegisterCart.url = f"{base_url}/carrinhos";

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
        # Use self.url defined in the class setup.
        response = requests.post(self.url, headers=headers, json=payload);
        
        assert response.status_code == 201;
        assert response.json()["message"] == "Cadastro realizado com sucesso";
        assert "_id" in response.json();

    def test_register_cart_duplicate_400(self, auth_token, produto_id):
        """Cenário 400: Não é permitido ter mais de 1 carrinho por usuário""";
        headers = {'Authorization': auth_token};
        payload = {"produtos": [{"idProduto": produto_id, "quantidade": 1}]};
        
        # Ensure that a cart already exists for this user.
        requests.post(self.url, headers=headers, json=payload);
        
        # Trying to register a second cart for the same user.
        response = requests.post(self.url, headers=headers, json=payload);
        
        assert response.status_code == 400;
        assert "Não é permitido ter mais de 1 carrinho" in response.json()["message"];

    def test_register_cart_token_absent_401(self):
        """Cenário 401: Token ausente, inválido ou expirado""";
        payload = {"produtos": [{"idProduto": "id_qualquer", "quantidade": 1}]};
        
        # Request without authorization headers using self.url
        response = requests.post(self.url, json=payload);
        
        assert response.status_code == 401;
        assert "Token de acesso ausente" in response.json()["message"];
        