from services.usuarios.usuarios_delete_service import deletar_usuario


def test_delete_usuario_sucesso(usuario_temporario):
    response = deletar_usuario(usuario_temporario)
    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "Registro excluído com sucesso"
