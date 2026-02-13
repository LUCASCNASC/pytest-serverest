import requests

class TestGetProdutosPorId:
    url_base = "https://serverest.dev/produtos"

    def test_buscar_produto_por_id_com_sucesso_200(self, auth_token):
        """Cenário 200: Produto encontrado com sucesso"""
        # 1. Preparação: Criar um produto para garantir que temos um ID válido para buscar
        payload = {
            "nome": "Produto Teste Busca ID",
            "preco": 50,
            "descricao": "Mousepad",
            "quantidade": 100
        }
        headers = {'Authorization': auth_token}
        res_post = requests.post(self.url_base, headers=headers, json=payload)
        produto_id = res_post.json()["_id"]

        # 2. Execução: Buscar o produto pelo ID gerado
        response = requests.get(f"{self.url_base}/{produto_id}")

        # 3. Validações baseadas no screenshot da documentação
        assert response.status_code == 200
        assert response.json()["nome"] == "Produto Teste Busca ID"
        assert "_id" in response.json()
        assert response.json()["_id"] == produto_id

    def test_buscar_produto_com_id_inexistente_400(self):
        """Cenário 400: Produto não encontrado"""
        # Usando um ID que segue o padrão de formato mas não existe no banco
        id_inexistente = "nonExistent12345"

        response = requests.get(f"{self.url_base}/{id_inexistente}")

        # Validação da mensagem de erro conforme o screenshot
        assert response.status_code == 400
        assert response.json()["message"] == "Produto não encontrado"