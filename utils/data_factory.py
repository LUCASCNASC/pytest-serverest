import uuid
from faker import Faker


def gerar_nome_produto():
    return f"Produto-{uuid.uuid4()}"

fake = Faker("pt_BR")

def gerar_usuario():
    return {
        "nome": fake.name(),
        "email": fake.email(),
        "password": "123456",
        "administrador": "true"
    }

def gerar_usuario_atualizado():
    return {
        "nome": fake.name(),
        "email": fake.email(),
        "password": "654321",
        "administrador": "false"
    }