# Deploy no Render

O `render.yaml` cria um Web Service Docker. Configure como secrets:

- `ACTA_MCP_API_KEY`
- `DATABASE_URL`
- `MONGODB_URI`
- `GEMINI_API_KEY` para embeddings do FAQ quando Qdrant estiver configurado
- `QDRANT_CLUSTER_ENDPOINT` e `QDRANT_API_KEY` são opcionais; sem eles, o FAQ usa busca lexical local

O serviço expõe a porta recebida em `PORT`, usa `/health` para health check e publica o MCP em `/mcp`.

Antes do deploy:

```powershell
docker build -t acta-mcp .
docker run --rm --env-file .env -p 8000:8000 acta-mcp
```

Use TLS no endpoint público do Render. Restrinja as credenciais PostgreSQL e MongoDB ao menor conjunto de permissões necessário e rotacione as chaves de serviço periodicamente.
