import requests

class TestCancelarCompra:
    url_cancelar = "https://serverest.dev/carrinhos/cancelar-compra"
    url_carrinhos = "https://serverest.dev/carrinhos"

    def test_cancelar_compra_com_sucesso_200(self, auth_token, produto_id):
        """Cenário 200: Registro excluído com sucesso (ou carrinho não encontrado)"""
        # 1. Preparação: Garante que o usuário tenha um carrinho ativo para cancelar
        headers = {'Authorization': auth_token}
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        }
        # Criamos o carrinho antes
        requests.post(self.url_carrinhos, headers=headers, json=payload)

        # 2. Execução: Cancela a compra
        response = requests.delete(self.url_cancelar, headers=headers)

        # 3. Validações conforme o screenshot da documentação
        assert response.status_code == 200
        # A API pode retornar "Registro excluído com sucesso" 
        # ou informar que não havia carrinho, ambos no status 200.
        assert "sucesso" in response.json()["message"] or "Não foi encontrado" in response.json()["message"]

    def test_cancelar_compra_sem_token_401(self):
        """Cenário 401: Tentativa de cancelar compra sem autenticação"""
        # Execução sem o header de Authorization
        response = requests.delete(self.url_cancelar)

        # Validação da mensagem de erro de autenticação
        assert response.status_code == 401
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais"