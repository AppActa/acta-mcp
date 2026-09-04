# Memória, embeddings e collections

## Modelo de persistência

MongoDB é a fonte da verdade. Qdrant é um índice de busca semântica que contém os
mesmos identificadores dos documentos persistidos. Se o upsert vetorial falhar, o
registro continua salvo no MongoDB com `indice_status=pendente` e é reprocessado na
inicialização seguinte, em lotes de até 100 itens por tipo.

| Finalidade | Collection MongoDB | Collection Qdrant |
| --- | --- | --- |
| Sessões | `memoria_sessoes` | não se aplica |
| Mensagens | `memoria_mensagens` | `memoria_mensagens` |
| Memórias longas | `memoria_usuario` | `memoria_usuario` |
| Consentimento | `memoria_consentimentos` | não se aplica |

Os nomes Qdrant são configuráveis por `QDRANT_MEMORY_MESSAGES_COLLECTION_NAME` e
`QDRANT_MEMORY_COLLECTION_NAME`. Eles devem corresponder aos nomes MongoDB acima
para manter o mapeamento operacional direto.

## Embeddings e índices

O módulo `infrastructure/qdrant/connection.py` centraliza a geração de embeddings:

- modelo: `gemini-embedding-2-preview`;
- dimensão fixa: **768**;
- distância Qdrant: `COSINE`;
- inferência Qdrant: desativada (`cloud_inference=False`).

O servidor valida collections existentes no startup. Uma collection com vetores
nomeados, dimensão diferente de 768 ou distância diferente de cosseno falha cedo,
evitando dados incompatíveis. As collections de memória recebem índices de payload
para `usuario_id`, `empresa_id`, `status`, `session_id` e `tipo`.

A collection FAQ `acta_faq` usa o mesmo embedding Gemini de 768 dimensões. O
catálogo `ACTA_DOCS` é sincronizado por hash de conteúdo, portanto apenas documentos
alterados recebem novo vetor.

## Ciclo de uma conversa

1. `memoria_garantir_sessao` cria ou recupera a sessão no MongoDB.
2. `memoria_salvar_mensagem` sanitiza PII, grava em `memoria_mensagens` e faz upsert
   do mesmo ID no Qdrant.
3. `memoria_obter_contexto` combina resumo incremental, mensagens recentes,
   preferências e busca semântica de memórias relacionadas à pergunta atual.
4. `memoria_material_resumo` retorna somente mensagens posteriores a
   `resumido_ate`; o `acta-ai` produz o texto e chama `memoria_atualizar_resumo`.
5. `memoria_encerrar_sessao` fecha apenas sessões que tenham mensagens. Uma sessão
   vazia não é listada nem resumida.

`memoria_listar_chats` lista as conversas não vazias do usuário autenticado. A API
do ACTA AI a expõe como `GET /listar_chats`.

## Memória longa e consentimento

`memoria_registrar` aceita `preferencia`, `ponto_relevante`, `decisao` e `objetivo`.
A busca `memoria_buscar` é semântica e sempre filtra `usuario_id`, `empresa_id` e
`status=ativa`; não usa regex para determinar relevância.

| Consentimento | Comportamento |
| --- | --- |
| `desativado` | Apaga memórias longas ativas e seus vetores. |
| `somente_explicitas` | Aceita memórias informadas explicitamente. |
| `automatica` | Também permite memórias inferidas, sujeitas à retenção. |

Mensagens possuem TTL em `ACTA_MEMORY_MESSAGE_RETENTION_DAYS`. Memórias inferidas
usam `ACTA_MEMORY_INFERRED_RETENTION_DAYS`; explícitas ficam ativas até exclusão ou
até a retenção informada pelo usuário. Expiração e exclusão removem o vetor antes de
eliminar ou desativar o registro canônico.

## Tools de memória

`memoria_garantir_sessao`, `memoria_salvar_mensagem`, `memoria_obter_contexto`,
`memoria_material_resumo`, `memoria_encerrar_sessao`, `memoria_listar_chats`,
`memoria_atualizar_resumo`, `memoria_registrar`, `memoria_buscar`,
`memoria_listar`, `memoria_excluir`, `memoria_obter_consentimento` e
`memoria_configurar_consentimento`.
