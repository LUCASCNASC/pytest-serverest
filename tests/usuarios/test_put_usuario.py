from services.usuarios.usuarios_post_service import post_usuario
from services.usuarios.usuarios_put_service import put_usuario
from utils.data_factory import gerar_usuario, gerar_usuario_atualizado


def test_put_usuario_success():
    # 1 - Criar usuário
    usuario = gerar_usuario()
    post_response = post_usuario(usuario)

    assert post_response.status_code == 201

    user_id = post_response.json()["_id"]

    # 2 - Atualizar usuário
    usuario_atualizado = gerar_usuario_atualizado()

    put_response = put_usuario(user_id, usuario_atualizado)

    body = put_response.json()

    # 3 - Validações
    assert put_response.status_code == 200
    assert body["message"] == "Registro alterado com sucesso"
