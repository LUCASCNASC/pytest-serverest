import requests;
from tests.conftest import base_url;

# Endpoint: GET /carrinhos/{id}

class TestSearchCartById:
    url_base = f"{base_url}/carrinhos";

    def test_search_cart_by_id_with_sucess_200(self, base_url, auth_token, produto_id):
        """Cenário 200: Carrinho encontrado com sucesso""";
        # Preparação: Criar um carrinho para garantir que temos um ID válido
        payload = {
            "produtos": [{"idProduto": produto_id, "quantidade": 1}]
        };
        res_post = requests.post(self.url_base, headers={'Authorization': auth_token}, json=payload);
        carrinho_id = res_post.json()["_id"];

        # Execução: Buscar o carrinho pelo ID gerado
        response = requests.get(f"{self.url_base}/{carrinho_id}");

        # Validações conforme a documentação
        assert response.status_code == 200;
        assert response.json()["_id"] == carrinho_id;
        assert "produtos" in response.json();
        assert "precoTotal" in response.json();

    def test_search_cart_by_id_inexistent_400(self, base_url):
        """Cenário 400: Carrinho não encontrado""";
        # Usando um ID com formato válido, mas que não existe no banco
        id_inexistente = "nonExistent12345" ;

        response = requests.get(f"{self.url_base}/{id_inexistente}");

        assert response.status_code == 400;
        assert response.json()["message"] == "Carrinho não encontrado";