import pytest;
import requests;

# Endpoint: Serverest GET /carrinhos

class TestSearchCarts:
    
    # Esta fixture centraliza a URL na classe usando a base_url injetada pelo Pytest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribuir o valor da string de URL ao atributo da classe
        TestSearchCarts.url = f"{base_url}/carrinhos";

    def test_list_cart_with_sucess_200(self, auth_token, produto_id):
        """Valida a listagem de carrinhos cadastrados (Status 200)"""
        # Preparação: Garante que existe pelo menos um carrinho na lista
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Create um carrinho vinculado ao seu usuário global usando self.url
        requests.post(self.url, headers={'Authorization': auth_token}, json=payload);

        # Execution: Lista todos os carrinhos
        response = requests.get(self.url);

        assert response.status_code == 200;
        assert "quantidade" in response.json();
        assert "carrinhos" in response.json();
        assert isinstance(response.json()["carrinhos"], list);
        
        # Valida a estrutura de um carrinho dentro da lista conforme o modelo
        if response.json()["quantidade"] > 0:
            carrinho = response.json()["carrinhos"][0];
            assert "produtos" in carrinho;
            assert "precoTotal" in carrinho;
            assert "idUsuario" in carrinho;
            assert "_id" in carrinho;
            