# ACTA MCP

Servidor MCP modular que centraliza acesso autorizado aos dados do ACTA, à memória
persistente e à base documental. O `acta-ai` usa este serviço por Streamable HTTP;
ele não acessa PostgreSQL, MongoDB ou Qdrant diretamente.

```text
ACTA AI → Streamable HTTP /mcp → Serviços de domínio → PostgreSQL / MongoDB / Qdrant
```

## Documentação

- [Arquitetura e ciclo de requisição](docs/architecture.md)
- [Autenticação e autorização](docs/authentication.md)
- [Catálogo de tools](docs/tools.md)
- [Memória, collections e busca semântica](docs/memory.md)
- [Configuração local e variáveis](docs/configuration.md)
- [Deploy](docs/deployment.md)

## Execução local

Pré-requisitos: Docker Desktop, Python 3.11+ e credenciais Qdrant e Gemini válidas.

```powershell
Copy-Item .env.example .env
docker compose up -d --wait
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:ACTA_AUTH_MODE = "disabled"
.\.venv\Scripts\python.exe -m acta_mcp.main --transport http
```

Endpoints locais:

- MCP: `http://127.0.0.1:8000/mcp`
- Saúde: `http://127.0.0.1:8000/health`

`ACTA_AUTH_MODE=disabled` serve somente para desenvolvimento e testes locais. Ele é
rejeitado em produção.

## Integração com o ACTA AI

```env
ACTA_MCP_URL=http://127.0.0.1:8000/mcp
ACTA_MCP_API_KEY=mesmo-segredo-do-servidor
ACTA_MCP_USUARIO_ID=1
ACTA_MCP_EMPRESA_ID=1
```

O cliente deve propagar identidade nos cabeçalhos HTTP. O servidor resolve o nível
de acesso a partir do usuário persistido e não aceita empresa, usuário ou permissão
como argumentos gerados por um modelo.

## Testes e qualidade

```powershell
docker compose up -d --wait
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check src tests
```

Os testes de integração requerem PostgreSQL, MongoDB, Qdrant e Gemini configurados.
