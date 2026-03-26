import pytest;
import requests;

# Endpoint: Serverest DELETE /carrinhos/concluir-compra

class TestConcludePurchase:
    
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Define the URLs at the class level using the actual string from the injected base_url.
        TestConcludePurchase.url_carrinhos = f"{base_url}/carrinhos";
        TestConcludePurchase.url_concluir = f"{TestConcludePurchase.url_carrinhos}/concluir-compra";

    def test_conclude_purchase_with_sucess_200(self, auth_token, produto_id):
        """Valida a conclusão de compra com carrinho ativo (Status 200)"""
        # 1. Preparation: Ensures the user has a cart to complete their purchase.
        headers = {'Authorization': auth_token};
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Create the cart before attempting to complete using the class URL.
        requests.post(self.url_carrinhos, headers=headers, json=payload);

        # 2. Execution: Completes the purchase.
        response = requests.delete(self.url_concluir, headers=headers);

        assert response.status_code == 200;
        assert response.json()["message"] in [
            "Registro excluído com sucesso", 
            "Não foi encontrado carrinho para esse usuário"
        ];

    def test_try_conclude_purchase_without_token_401(self):
        """Valida erro ao tentar concluir compra sem autenticação (Status 401)"""
        # Execution without the Authorization header using the class URL.
        response = requests.delete(self.url_concluir);

        assert response.status_code == 401;
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais";
        