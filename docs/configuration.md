# Configuração local e variáveis

## Serviços locais

`docker compose up -d --wait` cria somente PostgreSQL e MongoDB para desenvolvimento
 e testes. Gemini é usado por lições aprendidas e, com Qdrant, pelos embeddings do FAQ.

| Serviço | Variáveis principais |
| --- | --- |
| Autenticação | `ACTA_AUTH_MODE`, `ACTA_MCP_API_KEY` |
| PostgreSQL | `DATABASE_URL`, `ACTA_POSTGRES_POOL_MIN_SIZE`, `ACTA_POSTGRES_POOL_MAX_SIZE` |
| MongoDB | `MONGODB_URI`, `MONGODB_DATABASE`, `ACTA_MONGO_TIMEOUT_MS` |
| Gemini | `GEMINI_API_KEY` |
| FAQ semântico (opcional) | `QDRANT_CLUSTER_ENDPOINT`, `QDRANT_API_KEY`, `QDRANT_FAQ_COLLECTION` |

## Segurança

Em produção, use `ACTA_AUTH_MODE=api_key` e configure uma chave forte em
`ACTA_MCP_API_KEY`. O modo `disabled` é proibido quando `ACTA_ENV=production`.
Mantenha `DATABASE_URL`, `MONGODB_URI`, Gemini e observabilidade fora
do controle de versão.

## Execução

```powershell
Copy-Item .env.example .env
docker compose up -d --wait
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m acta_mcp.main --transport http
```

Para testar o transporte stdio, use `ACTA_AUTH_MODE=disabled`; ele injeta os IDs
definidos em `ACTA_DEFAULT_USUARIO_ID` e `ACTA_DEFAULT_EMPRESA_ID`.
