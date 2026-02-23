import requests;
from tests.conftest import base_url;

# Endpoint: POST /login

class TestLogin:
    url = f"{base_url}/login";

    def test_login_with_sucess_200(self, base_url, usuario_global):
        """Valida login com credenciais válidas (Status 200)""";
        payload = {
            "email": usuario_global["email"],
            "password": usuario_global["password"]
        };
        response = requests.post(self.url, json=payload);
        
        assert response.status_code == 200;
        assert response.json()["message"] == "Login realizado com sucesso";
        assert "authorization" in response.json();

    def test_login_email_password_invalids_401(self, base_url):
        """Valida erro ao logar com credenciais inexistentes (Status 401)""";
        payload = {
            "email": "email_inexistente_@qa.com",
            "password": "senha_errada"
        };
        response = requests.post(self.url, json=payload);
        
        assert response.status_code == 401;
        assert response.json()["message"] == "Email e/ou senha inválidos";