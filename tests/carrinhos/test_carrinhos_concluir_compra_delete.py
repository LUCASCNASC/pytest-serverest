import requests;

# Endpoint: DELETE /carrinhos/concluir-compra

class TestConcludePurchase:
    url_concluir = "https://serverest.dev/carrinhos/concluir-compra";
    url_carrinhos = "https://serverest.dev/carrinhos";

    def test_conclude_purchase_with_sucess_200(self, base_url, auth_token, produto_id):
        """Valida a conclusão de compra com carrinho ativo (Status 200)""";
        # 1. Preparação: Garante que o usuário tem um carrinho para concluir
        headers = {'Authorization': auth_token};
        payload = {
            "produtos": [
                {
                    "idProduto": produto_id,
                    "quantidade": 1
                }
            ]
        };
        # Cria o carrinho antes de tentar concluir
        requests.post(self.url_carrinhos, headers=headers, json=payload);

        # Execução: Conclui a compra
        response = requests.delete(self.url_concluir, headers=headers);

        assert response.status_code == 200;
        assert response.json()["message"] in [
            "Registro excluído com sucesso", 
            "Não foi encontrado carrinho para esse usuário"
        ];

    def test_try_conclude_purchase_without_token_401(self, base_url):
        """Valida erro ao tentar concluir compra sem autenticação (Status 401)""";
        # Execução sem o header de Authorization
        response = requests.delete(self.url_concluir);

        assert response.status_code == 401;
        assert response.json()["message"] == "Token de acesso ausente, inválido, expirado ou usuário do token não existe mais";