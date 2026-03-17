import pytest;
import requests;

# Endpoint: Serverest GET /produtos/{id}

class TestSearchProductById:
    
    # Esta fixture resolve o problema da URL na classe, injetando a string do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribui o valor da string de URL ao atributo da classe
        TestSearchProductById.url_base = f"{base_url}/produtos";

    def test_search_product_by_id_with_sucess_200(self, auth_token):
        """Cenário 200: Produto encontrado com sucesso""";
        # Adicionar um número aleatório ao nome para evitar conflitos de duplicidade
        nome_dinamico = f"Produto Teste {fake.random_number(digits=5)}";
        payload = {
            "nome": nome_dinamico,
            "preco": 50,
            "descricao": "Mousepad",
            "quantidade": 100
        };
        headers = {'Authorization': auth_token};
        res_post = requests.post(self.url_base, headers=headers, json=payload);
        
        # Opcional: print para debug se falhar de novo
        if res_post.status_code != 201:
             print(f"Erro no setup: {res_post.json()}");

        produto_id = res_post.json()["_id"];

        # Execução: Buscar o produto pelo ID gerado
        response = requests.get(f"{self.url_base}/{produto_id}");

        assert response.status_code == 200;
        assert response.json()["nome"] == "Produto Teste Busca ID";
        assert "_id" in response.json();
        assert response.json()["_id"] == produto_id;

    def test_search_product_with_id_inexistent_400(self):
        """Cenário 400: Produto não encontrado""";
        # Usar um ID que segue o padrão de formato mas não existe no banco
        id_inexistente = "nonExistent12345";

        response = requests.get(f"{self.url_base}/{id_inexistente}");

        assert response.status_code == 400;
        assert response.json()["message"] == "Produto não encontrado";
        