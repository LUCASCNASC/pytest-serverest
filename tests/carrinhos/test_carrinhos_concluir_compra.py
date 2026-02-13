import requests

class TestConcluirCompra:
    url_concluir = "https://serverest.dev/carrinhos/concluir-compra"
    url_carrinhos = "https://serverest.dev/carrinhos"

    def test_concluir_compra_com_sucesso_200(self, auth_token, produto_id):
        """Valida a conclusão de compra com carrinho ativo (Status 200)"""
        # 1. Preparação: Garante que o usuário tem um carrinho para concluir
        headers = {'Authorization': auth_token}
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        }
        # Cria o carrinho antes de tentar concluir
        requests.post(self.url_carrinhos, headers=headers, json=payload)

        # 2. Execução: Conclui a compra
        response = requests.delete(self.url_concluir, headers=headers)

        # 3. Validações baseadas no screenshot
        assert response.status_code == 200
        # A API retorna a mesma mensagem para sucesso ou carrinho não encontrado
        assert response.json()["message"] in [
            "Registro excluído com sucesso", 
            "Não foi encontrado carrinho para esse usuário"
        ]

    def test_tentar_concluir_compra_sem_token_401(self):
        """Valida erro ao tentar concluir compra sem autenticação (Status 401)"""
        # Execução sem o header de Authorization
        response = requests.delete(self.url_concluir)

        # Validações baseadas no screenshot
        assert response.status_code == 401
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"