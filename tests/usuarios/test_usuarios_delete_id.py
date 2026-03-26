import pytest;
import requests;
from faker import Faker;

fake = Faker();

class TestDeleteUserById:
    
    # This fixture solves the URL problem. It runs once for the class.
    # and inject the correct string from conftest.py
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Assign the URL string value to the class attribute
        TestDeleteUserById.url_base = f"{base_url}/usuarios"

    def test_delete_user_with_sucess_200(self):
        """Cenário 200: Registro excluído com sucesso"""
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        # Now self.url_base will be 'https://serverest.dev/usuarios'
        res_post = requests.post(self.url_base, json=payload)
        user_id = res_post.json()["_id"]

        response = requests.delete(f"{self.url_base}/{user_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Registro excluído com sucesso"

    def test_delete_user_with_active_cart_400(self):
        """Cenário 400: Não é permitido excluir usuário com carrinho ativo"""
        user_id_com_carrinho = "0uxuPY0cbmQhpEz1"
        
        response = requests.delete(f"{self.url_base}/{user_id_com_carrinho}")

        assert response.status_code == 400
        assert response.json()["message"] == "Não é permitido excluir usuário com carrinho cadastrado"

    def test_delete_user_inexistent_200(self):
        """Cenário 200: Nenhum registro excluído (ID não encontrado)"""
        id_inexistente = "ID_QUE_NAO_EXISTE"
        
        response = requests.delete(f"{self.url_base}/{id_inexistente}")

        assert response.status_code == 200
        assert response.json()["message"] == "Nenhum registro excluído"
        