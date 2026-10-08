# Testes da API ServeRest com pytest

Projeto de testes baseado na especificação OpenAPI em `serverest.json`. A suíte
combina verificações locais do contrato com testes de integração contra a API
ServeRest.

## Requisitos

- Python 3.9 ou superior
- Acesso à internet para os testes de integração

## Instalação

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Executar

Execute toda a suíte:

```powershell
pytest
```

Para ver cada método e rota como um caso separado no relatório:

```powershell
pytest -v tests/test_api_routes.py
```

Execute somente as verificações locais da especificação:

```powershell
pytest tests/test_openapi_contract.py
```

Por padrão, os testes de integração chamam `https://serverest.dev`. Para usar
uma instância local ou outro ambiente compatível, defina `SERVEREST_BASE_URL`:

```powershell
$env:SERVEREST_BASE_URL = "http://localhost:3000"
pytest
```

Os fluxos de integração criam usuários e produtos com identificadores únicos e
tentam removê-los ao final. Não use credenciais reais nesses testes.

A suíte possui um caso positivo nomeado por operação documentada no OpenAPI:
login; listagem e CRUD de usuários e produtos; listagem, criação e consulta de
carrinhos; e cancelamento e conclusão de compras. Os casos estão em
`tests/test_api_routes.py`; use `pytest -v` para auditar os nomes e resultados
individualmente. Verificações do arquivo OpenAPI ficam separadas em
`tests/test_openapi_contract.py`.
