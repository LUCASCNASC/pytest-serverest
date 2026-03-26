import pytest;
import requests;

# Endpoint: Serverest GET /carrinhos

class TestSearchCarts:
    
    # This fixture centralizes the URL in the class using the base_url injected by Pytest.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute.
        TestSearchCarts.url = f"{base_url}/carrinhos";

    def test_list_cart_with_sucess_200(self, auth_token, produto_id):
        """Valida a listagem de carrinhos cadastrados (Status 200)"""
        # Preparation: Ensure there is at least one cart in the list.
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Create a shopping cart linked to your global user using self.url.
        requests.post(self.url, headers={'Authorization': auth_token}, json=payload);

        # Execution: List all carts.
        response = requests.get(self.url);

        assert response.status_code == 200;
        assert "quantidade" in response.json();
        assert "carrinhos" in response.json();
        assert isinstance(response.json()["carrinhos"], list);
        
        # Validate the structure of a cart within the list according to the model
        if response.json()["quantidade"] > 0:
            carrinho = response.json()["carrinhos"][0];
            assert "produtos" in carrinho;
            assert "precoTotal" in carrinho;
            assert "idUsuario" in carrinho;
            assert "_id" in carrinho;
            