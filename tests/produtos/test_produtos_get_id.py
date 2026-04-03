import pytest;
import requests;

# Endpoint: Serverest GET /produtos/{id}

class TestSearchProductById:
    
    # This fixture solves the URL problem in the class by injecting the conftest string.
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute
        TestSearchProductById.url_base = f"{base_url}/produtos";

    def test_search_product_by_id_with_sucess_200(self, auth_token):
        """Status 200: Produto encontrado com sucesso""";
        # Add a random number to the name to avoid duplicate conflicts.
        nome_dinamico = f"Produto Teste {fake.random_number(digits=5)}";
        payload = {
            "nome": nome_dinamico,
            "preco": 50,
            "descricao": "Mousepad",
            "quantidade": 100
        };
        headers = {'Authorization': auth_token};
        res_post = requests.post(self.url_base, headers=headers, json=payload);
        
        # Optional: print for debugging if it fails again.
        if res_post.status_code != 201:
             print(f"Erro no setup: {res_post.json()}");

        produto_id = res_post.json()["_id"];

        # Execution: Search for the product using the generated ID.
        response = requests.get(f"{self.url_base}/{produto_id}");

        assert response.status_code == 200;
        assert response.json()["nome"] == "Produto Teste Busca ID";
        assert "_id" in response.json();
        assert response.json()["_id"] == produto_id;

    def test_search_product_with_id_inexistent_400(self):
        """Status 400: Produto não encontrado""";
        # Using an ID that follows the format pattern but does not exist in the database.
        id_inexistente = "nonExistent12345";

        response = requests.get(f"{self.url_base}/{id_inexistente}");

        assert response.status_code == 400;
        assert response.json()["message"] == "Produto não encontrado";
        