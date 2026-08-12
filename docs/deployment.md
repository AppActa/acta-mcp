# Deploy no Render

O `render.yaml` cria um Web Service Docker. Configure como secrets:

- `ACTA_MCP_API_KEY`
- `DATABASE_URL`
- `MONGODB_URI`
- `QDRANT_API_KEY`
- `QDRANT_CLUSTER_ENDPOINT`

O serviço expõe a porta recebida em `PORT`, usa `/health` para health check e publica o MCP em `/mcp`.

Antes do deploy:

```powershell
docker build -t acta-mcp .
docker run --rm --env-file .env -p 8000:8000 acta-mcp
```

Use TLS no endpoint público do Render. Restrinja as credenciais PostgreSQL, MongoDB e Qdrant ao menor conjunto de permissões necessário e rotacione as chaves de serviço periodicamente.
