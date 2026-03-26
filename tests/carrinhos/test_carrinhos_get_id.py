import pytest;
import requests;

# Endpoint: Serverest GET /carrinhos/{id}

class TestSearchCartById:
    
    # This fixture ensures that the URL is correctly constructed using the base_url from conftest.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the correct value to the class variable for use in the tests.
        TestSearchCartById.url_base = f"{base_url}/carrinhos";

    def test_search_cart_by_id_with_sucess_200(self, auth_token, produto_id):
        """Cenário 200: Carrinho encontrado com sucesso""";
        # Preparation: Create a cart to ensure we have a valid ID.
        payload = {
            "produtos": [{"idProduto": produto_id, "quantidade": 1}]
        };
        res_post = requests.post(
            self.url_base, 
            headers={'Authorization': auth_token}, 
            json=payload
        );
        carrinho_id = res_post.json()["_id"];

        # Execution: Retrieve the cart by the ID generated using self.url_base.
        response = requests.get(f"{self.url_base}/{carrinho_id}");

        # Validations as per documentation.
        assert response.status_code == 200;
        assert response.json()["_id"] == carrinho_id;
        assert "produtos" in response.json();
        assert "precoTotal" in response.json();

    def test_search_cart_by_id_inexistent_400(self):
        """Cenário 400: Carrinho não encontrado"""
        # Using an ID with a valid format, but which does not exist in the database.
        id_inexistente = "nonExistent12345";

        response = requests.get(f"{self.url_base}/{id_inexistente}");

        assert response.status_code == 400;
        assert response.json()["message"] == "Carrinho não encontrado";
        