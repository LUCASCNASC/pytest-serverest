from services.usuarios.usuarios_post_service import usuarios
from services.usuarios.usuarios_get_by_id_service import get_usuario_by_id

def test_get_usuario_by_id_success():
    # cria usuário
    post_response = usuarios()
    post_body = post_response.json()

    usuario_id = post_body["_id"]

    # busca usuário pelo id
    get_response = get_usuario_by_id(usuario_id)
    body = get_response.json()

    assert get_response.status_code == 200
    assert body["_id"] == usuario_id
    assert "nome" in body
    assert "email" in body
    assert "administrador" in body
    