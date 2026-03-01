import pytest
import requests

# Endpoint: POST /login

class TestLogin:
    
    # Esta fixture garante que a URL seja montada corretamente usando a base_url do conftest
    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, base_url):
        # Atribui o valor da string de URL ao atributo da classe para uso nos métodos
        TestLogin.url = f"{base_url}/login"

    def test_login_with_sucess_200(self, usuario_global):
        """Valida login com credenciais válidas (Status 200)"""
        payload = {
            "email": usuario_global["email"],
            "password": usuario_global["password"]
        }
        # Agora self.url é uma string válida injetada pelo setup_class
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 200
        assert response.json()["message"] == "Login realizado com sucesso"
        assert "authorization" in response.json()

    def test_login_email_password_invalids_401(self):
        """Valida erro ao logar com credenciais inexistentes (Status 401)"""
        payload = {
            "email": "email_inexistente_@qa.com",
            "password": "senha_errada"
        }
        response = requests.post(self.url, json=payload)
        
        assert response.status_code == 401
        assert response.json()["message"] == "Email e/ou senha inválidos"
        