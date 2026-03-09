import pytest;
import requests;
from faker import Faker;

# Endpoint: PUT /produtos/{id}

fake = Faker()

class TestUpdateProductById:
    
    # Esta fixture resolve o problema da URL na classe, injetando a string do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribui o valor da string de URL ao atributo da classe
        TestUpdateProductById.url_base = f"{base_url}/produtos";

    def test_change_product_with_sucess_200(self, auth_token, produto_id):
        """Cenário 200: Registro alterado com sucesso""";
        headers = {'Authorization': auth_token};
        payload = {
            "nome": f"Editado {fake.word()} {fake.random_number()}",
            "preco": 99,
            "descricao": "Item Editado",
            "quantidade": 50
        };
        # Usa self.url_base definido no setup da classe
        response = requests.put(f"{self.url_base}/{produto_id}", headers=headers, json=payload);

        assert response.status_code == 200;
        assert response.json()["message"] == "Registro alterado com sucesso";

    def test_register_product_via_put_201(self, auth_token):
        """Cenário 201: Cadastro realizado com sucesso (ID não encontrado)""";
        headers = {'Authorization': auth_token};
        id_inexistente = f"novo_prod_{fake.random_number()}";
        payload = {
            "nome": f"Novo via PUT {fake.word()}",
            "preco": 150,
            "descricao": "Criado via PUT",
            "quantidade": 10
        };
        response = requests.put(f"{self.url_base}/{id_inexistente}", headers=headers, json=payload);

        assert response.status_code == 201;
        assert response.json()["message"] == "Cadastro realizado com sucesso";
        assert "_id" in response.json();

    def test_put_name_duplicate_400(self, auth_token, produto_id):
        """Cenário 400: Já existe produto com esse nome""";
        headers = {'Authorization': auth_token};
        
        # Criamos um segundo produto 'B' para tentar roubar o nome dele
        nome_em_uso = f"Nome Ocupado {fake.random_number()}";
        requests.post(self.url_base, headers=headers, json={
            "nome": nome_em_uso, "preco": 10, "descricao": "D", "quantidade": 1
        });

        # Tentamos editar o produto 'A' (produto_id) usando o nome do produto 'B'
        payload_conflito = {
            "nome": nome_em_uso,
            "preco": 50,
            "descricao": "Conflito",
            "quantidade": 5
        };
        response = requests.put(f"{self.url_base}/{produto_id}", headers=headers, json=payload_conflito);

        assert response.status_code == 400;
        assert response.json()["message"] == "Já existe produto com esse nome";

    def test_put_token_empty_401(self):
        """Cenário 401: Token ausente ou inválido""";
        # Requisição enviada sem header de autorização usando self.url_base
        response = requests.put(f"{self.url_base}/qualquer_id", json={});
        
        assert response.status_code == 401;
        assert "Token de acesso ausente" in response.json()["message"];

    def test_put_without_permission_admin_403(self, base_url):
        """Cenário 403: Rota exclusiva para administradores""";
        # 1. Criar e logar com usuário comum (admin: false)
        email_comum = fake.email();
        url_usuarios = f"{base_url}/usuarios";
        url_login = f"{base_url}/login";

        requests.post(url_usuarios, json={
            "nome": "Common", "email": email_comum, "password": "123", "administrador": "false"
        });
        login_res = requests.post(url_login, 
                                  json={"email": email_comum, "password": "123"});
        token_comum = login_res.json()["authorization"];
        
        # 2. Tentar editar produto com token sem permissão
        headers = {'Authorization': token_comum};
        response = requests.put(f"{self.url_base}/id_qualquer", headers=headers, json={});
        
        assert response.status_code == 403;
        assert response.json()["message"] == "Rota exclusiva para administradores";
        