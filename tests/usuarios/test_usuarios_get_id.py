import requests;
from faker import Faker;

# Endpoint: GET /usuarios/{id}

fake = Faker();

class TestGetUsuariosPorId:
    url_base = "https://serverest.dev/usuarios";

    def test_search_user_by_id_with_success_200(self):
        """Valida a busca de um usuário por um ID válido (Status 200)""";
        # Primeiro, cadastramos um usuário para garantir que o ID existe
        payload_cadastro = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        };
        cadastro_res = requests.post(self.url_base, json=payload_cadastro);
        user_id = cadastro_res.json()["_id"];

        # Agora, buscamos esse ID específico
        response = requests.get(f"{self.url_base}/{user_id}");
        
        assert response.status_code == 200;
        assert response.json()["nome"] == payload_cadastro["nome"];
        assert response.json()["_id"] == user_id;
        assert "email" in response.json();

    def test_search_user_by_id_inexistent_400(self):
        """Valida a busca por um ID que não consta no sistema (Status 400)""";
        # Usando um ID com formato válido (16 caracteres), mas que não existe
        id_inexistente = "nonExistent12345";

        response = requests.get(f"{self.url_base}/{id_inexistente}");

        # Se houver erro de chave, o print abaixo ajudará a ver o que a API retornou
        if response.status_code != 400:
            print(f"\nDebug - Status: {response.status_code}");
            print(f"Debug - Body: {response.json()}");

        assert response.status_code == 400;
        assert response.json()["message"] == "Usuário não encontrado";