# Arquitetura

## Objetivo e fronteiras

O ACTA MCP é um monólito modular. Ele publica operações de negócio por MCP e mantém
as integrações de infraestrutura fora da camada conversacional. Agentes, prompts,
roteamento e resposta final pertencem ao `acta-ai`; este repositório não escolhe qual
tool um agente deve chamar.

| Camada | Responsabilidade |
| --- | --- |
| `core` | Configuração, contexto de requisição, autenticação, erros e execução auditada. |
| `modules` | Schemas, services, repositories e tools por domínio. |
| `infrastructure` | Clientes e adaptadores de PostgreSQL, MongoDB, Qdrant e observabilidade. |
| `registry.py` | Registro único de tools, resources e prompts. |
| `server.py` | Container, lifecycle ASGI, endpoint de saúde e transporte MCP. |

## Ciclo HTTP

```mermaid
flowchart TD
    A[POST /mcp] --> B[Valida Bearer e cabeçalhos ACTA]
    B --> C[Resolve usuário e permissões]
    C --> D[Cria RequestContext]
    D --> E[Tool MCP e schema]
    E --> F[Service de domínio]
    F --> G[Repositório PostgreSQL, MongoDB ou Qdrant]
    G --> H[Resposta estruturada]
    H --> I[Auditoria e trace_id]
```

Em cada inicialização HTTP, o lifecycle abre o pool PostgreSQL, verifica MongoDB,
valida/cria os índices de memória, sincroniza a documentação RAG e prepara os índices
das skills e lições aprendidas. `GET /health` verifica PostgreSQL, MongoDB e Qdrant;
retorna `503` se algum deles estiver indisponível.

## Fontes de dados

- **PostgreSQL:** entidades transacionais do ACTA, permissões, ciclos, tarefas,
  colaboradores, treinamentos e predições.
- **MongoDB:** formulários, skills, lições aprendidas e fonte oficial das sessões,
  mensagens, consentimentos e memórias do usuário.
- **Qdrant:** índice vetorial da documentação FAQ e da memória. Não é fonte oficial
  de dados de memória.

## Isolamento e autorização

O `RequestContext` contém `usuario_id`, `empresa_id`, permissões e `trace_id`.
Services e repositories aplicam esses valores nas consultas. Em especial, a memória
filtra simultaneamente usuário e empresa em MongoDB e Qdrant. O cliente não escolhe
o nível de acesso; ele é derivado de `usuario_sistema.tipo_usuario`.

Consulte [Autenticação](authentication.md) para os níveis e cabeçalhos exigidos.
