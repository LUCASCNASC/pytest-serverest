import pytest;
import requests;

# Endpoint: Serverest GET /produtos

class TestSearchProducts:
    
    # This fixture solves the URL problem in the class by injecting the conftest string.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute
        TestSearchProducts.url = f"{base_url}/produtos";

    def test_list_products_with_sucess_200(self):
        """Valida a listagem de produtos com sucesso (Status 200)""";
        # Execution of the GET request using the self.url defined in the setup.
        response = requests.get(self.url);

        assert response.status_code == 200;
        
        response_data = response.json();
        
        assert "quantidade" in response_data;
        assert "produtos" in response_data;
        assert isinstance(response_data["produtos"], list);

        # If there are products in the list, validate the structure of the first item.
        if response_data["quantidade"] > 0:
            produto = response_data["produtos"][0];
            assert "nome" in produto;
            assert "preco" in produto;
            assert "descricao" in produto;
            assert "quantidade" in produto;
            assert "_id" in produto;
            