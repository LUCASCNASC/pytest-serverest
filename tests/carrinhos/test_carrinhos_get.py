import requests;

# Endpoint: GET /carrinhos

class TestGetCarrinhos:
    url = "https://serverest.dev/carrinhos";

    def test_list_cart_with_sucess_200(self, auth_token, produto_id):
        """Valida a listagem de carrinhos cadastrados (Status 200)""";
        # Preparação: Garante que existe pelo menos um carrinho na lista
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Cria um carrinho vinculado ao seu usuário global
        requests.post(self.url, headers={'Authorization': auth_token}, json=payload);

        # Execução: Lista todos os carrinhos
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