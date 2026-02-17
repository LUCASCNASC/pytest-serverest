import requests;

class TestGetProdutos:
    url = "https://serverest.dev/produtos";

    def test_list_products_with_sucess_200(self):
        """Valida a listagem de produtos com sucesso (Status 200)""";
        # Execução da requisição GET
        response = requests.get(self.url);

        assert response.status_code == 200;
        
        response_data = response.json();
        
        assert "quantidade" in response_data;
        assert "produtos" in response_data;
        assert isinstance(response_data["produtos"], list);

        # Se houver produtos na lista, valida a estrutura do primeiro item
        if response_data["quantidade"] > 0:
            produto = response_data["produtos"][0];
            assert "nome" in produto;
            assert "preco" in produto;
            assert "descricao" in produto;
            assert "quantidade" in produto;
            assert "_id" in produto;