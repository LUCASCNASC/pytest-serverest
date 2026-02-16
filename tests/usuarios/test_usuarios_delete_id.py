import requests
from faker import Faker

fake = Faker()

class TestDeleteUsuarios:
    url_base = "https://serverest.dev/usuarios"

    def test_delete_user_with_sucess_200(self):
        """Cenário 200: Registro excluído com sucesso"""
        # Primeiro, cadastramos um usuário para garantir que temos um ID válido para deletar
        payload = {
            "nome": fake.name(),
            "email": fake.email(),
            "password": "teste",
            "administrador": "true"
        }
        res_post = requests.post(self.url_base, json=payload)
        user_id = res_post.json()["_id"]

        # Agora, executamos a exclusão
        response = requests.delete(f"{self.url_base}/{user_id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Registro excluído com sucesso"

    def test_delete_user_with_active_cart_400(self):
        """Cenário 400: Não é permitido excluir usuário com carrinho ativo"""
        # Nota: Para este teste falhar com 400, precisaríamos vincular um carrinho ao ID.
        # No ServeRest, o ID '0uxuPY0cbmQhpEz1' costuma ter dependências em ambientes de demonstração.
        
        user_id_com_carrinho = "0uxuPY0cbmQhpEz1" 
        
        # Tentativa de exclusão de usuário que possui vínculo (ex: carrinho)
        response = requests.delete(f"{self.url_base}/{user_id_com_carrinho}")

        assert response.status_code == 400
        assert response.json()["message"] == "Não é permitido excluir usuário com carrinho cadastrado"

    def test_delete_user_inexistent_200(self):
        """Cenário 200: Nenhum registro excluído (ID não encontrado)"""
        # O ServeRest retorna 200 mesmo se o ID não existir, informando que nada foi feito
        id_inexistente = "ID_QUE_NAO_EXISTE"
        
        response = requests.delete(f"{self.url_base}/{id_inexistente}")

        assert response.status_code == 200
        assert response.json()["message"] == "Nenhum registro excluído"