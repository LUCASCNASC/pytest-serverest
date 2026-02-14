import requests

class TestGetCarrinhosPorId:
    url_base = "https://serverest.dev/carrinhos"

    def test_buscar_carrinho_por_id_com_sucesso_200(self, auth_token, produto_id):
        """Cenário 200: Carrinho encontrado com sucesso"""
        # Preparação: Criar um carrinho para garantir que temos um ID válido
        payload = {
            "produtos": [{"idProduto": produto_id, "quantidade": 1}]
        }
        res_post = requests.post(self.url_base, headers={'Authorization': auth_token}, json=payload)
        carrinho_id = res_post.json()["_id"]

        # Execução: Buscar o carrinho pelo ID gerado
        response = requests.get(f"{self.url_base}/{carrinho_id}")

        # Validações conforme a documentação
        assert response.status_code == 200
        assert response.json()["_id"] == carrinho_id
        assert "produtos" in response.json()
        assert "precoTotal" in response.json()

    def test_buscar_carrinho_com_id_inexistente_400(self):
        """Cenário 400: Carrinho não encontrado"""
        # Usando um ID com formato válido, mas que não existe no banco
        id_inexistente = "nonExistent12345" 

        response = requests.get(f"{self.url_base}/{id_inexistente}")

        assert response.status_code == 400
        assert response.json()["message"] == "Carrinho não encontrado"