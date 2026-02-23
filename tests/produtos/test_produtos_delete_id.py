import requests;
from tests.conftest import base_url;
from faker import Faker;

# Endpoint: DELETE /produtos/{id}

fake = Faker();

class TestDeleteProductById:
    url_base = f"{base_url}/produtos";

    def test_delete_product_with_sucess_200(self, base_url, auth_token):
        """Cenário 200: Registro excluído com sucesso""";
        # Preparação: Criar um produto para garantir um ID válido
        headers = {'Authorization': auth_token};
        payload = {
            "nome": f"Produto para Deletar {fake.random_number()}",
            "preco": 10,
            "descricao": "Teste Delete",
            "quantidade": 1
        };
        res_post = requests.post(self.url_base, headers=headers, json=payload);
        produto_id = res_post.json()["_id"];

        # Execução: Excluir o produto
        response = requests.delete(f"{self.url_base}/{produto_id}", headers=headers);

        assert response.status_code == 200;
        assert response.json()["message"] == "Registro excluído com sucesso";

    def test_delete_product_linked_to_cart_400(self, base_url, auth_token, produto_id):
        """Cenário 400: Não é permitido excluir produto que faz parte de carrinho""";
        headers = {'Authorization': auth_token};
        
        # Preparação: Colocar o produto em um carrinho
        url_carrinhos = "https://serverest.dev/carrinhos";
        payload_carrinho = {
            "produtos": [{"idProduto": produto_id, "quantidade": 1}]
        };
        requests.post(url_carrinhos, headers=headers, json=payload_carrinho);

        # Execução: Tentar excluir o produto que está no carrinho
        response = requests.delete(f"{self.url_base}/{produto_id}", headers=headers);

        assert response.status_code == 400;
        assert response.json()["message"] == "Não é permitido excluir produto que faz parte de carrinho";

    def test_delete_product_without_token_401(self, base_url):
        """Cenário 401: Token ausente ou inválido""";
        response = requests.delete(f"{self.url_base}/id_qualquer");
        
        assert response.status_code == 401;
        assert "Token de acesso ausente" in response.json()["message"];

    def test_delete_product_without_permission_admin_403(self, base_url):
        """Cenário 403: Rota exclusiva para administradores""";
        # Criar e logar com usuário comum (admin: false)
        email_comum = fake.email();
        requests.post("https://serverest.dev/usuarios", json={
            "nome": "Common User", "email": email_comum, "password": "123", "administrador": "false"
        });
        login_res = requests.post("https://serverest.dev/login", 
                                  json={"email": email_comum, "password": "123"});
        token_comum = login_res.json()["authorization"];
        
        headers = {'Authorization': token_comum};
        response = requests.delete(f"{self.url_base}/id_qualquer", headers=headers);
        
        assert response.status_code == 403;
        assert response.json()["message"] == "Rota exclusiva para administradores";