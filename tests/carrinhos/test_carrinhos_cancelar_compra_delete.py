import pytest;
import requests;

# Endpoint: Serverest DELETE /carrinhos/cancelar-compra
class TestCancelPurchase:
    
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Define the URLs at the class level using the actual base_url string.
        TestCancelPurchase.url_carrinhos = f"{base_url}/carrinhos";
        TestCancelPurchase.url_cancelar = f"{TestCancelPurchase.url_carrinhos}/cancelar-compra";

    def test_cancel_purchase_with_sucesso_200(self, auth_token, produto_id):
        """Status 200: Registro excluído com sucesso (ou carrinho não encontrado)""";
        # Preparação: Garante que o usuário tenha um carrinho ativo para cancelar
        headers = {'Authorization': auth_token};
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Create the cart first using the URL defined in the class.
        requests.post(self.url_carrinhos, headers=headers, json=payload);

        # Execution: Cancel the purchase.
        response = requests.delete(self.url_cancelar, headers=headers);

        assert response.status_code == 200;
        assert "sucesso" in response.json()["message"] or "Não foi encontrado" in response.json()["message"];

    def test_cancel_purchase_without_token_401(self):
        """Status 401: Tentativa de cancelar compra sem autenticação"""
        # Execution without the Authorization header using the class URL.
        response = requests.delete(self.url_cancelar);

        assert response.status_code == 401;
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais";
        