# Arquitetura

O ACTA MCP é um monólito modular com separação hexagonal:

- `core`: configuração, autenticação, contexto, logging e tratamento de erros;
- `infrastructure`: pools e adaptadores PostgreSQL/MongoDB/Qdrant, serialização e auditoria;
- `modules`: contratos, repositórios, serviços e portas MCP por domínio;
- `resources` e `prompts`: contexto legível e fluxos reutilizáveis;
- `registry.py`: composição central das 28 tools;
- `server.py`: container, lifecycle e transporte.

## Fluxo de chamada

```mermaid
flowchart TD
    A["POST /mcp"] --> B["Bearer + headers ACTA"]
    B --> C["Contexto autenticado"]
    C --> D["Validação da entrada"]
    D --> E["Serviço de domínio"]
    E --> F["Validação de acesso ao tenant"]
    F --> G["Repositório PostgreSQL/MongoDB/Qdrant"]
    G --> H["Resultado estruturado MCP"]
    H --> I["Auditoria com trace_id"]
```

O `acta-ai` continua responsável por LangGraph, roteamento, prompts, memória e resposta final. O MCP não contém agentes nem LLM.
