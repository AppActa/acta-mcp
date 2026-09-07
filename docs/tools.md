# Catálogo de tools

As tools recebem somente argumentos do domínio. Identidade, empresa e permissões vêm
do `RequestContext` autenticado e nunca de parâmetros decididos pelo modelo.

| Domínio | Operações |
| --- | --- |
| Ciclos | visão geral, problemas, causas raiz, Ishikawa, riscos, participantes, treinamentos e escrita autorizada de causas/itens. |
| Tarefas | consultas, atrasos, responsáveis, alertas, relatórios e escrita autorizada. |
| Colaboradores | consulta, detalhes seguros, participação, carga e sugestão de realocação. |
| Formulários | listagem, respostas, resumo, rascunho, perguntas e publicação. |
| Relatórios | contexto consolidado de um ciclo para geração pelo ACTA AI. |
| Predições | riscos, estimativas, sobrecarga, metas, anomalias e recorrência com amostra mínima. |
| RAG | `faq_retriever`, busca semântica no catálogo `ACTA_DOCS`. |
| Memória | sessões, mensagens, resumo, busca, consentimento e chats. Veja [Memória](memory.md). |
| Skills | criação, consulta, listagem e exclusão de instruções privadas de apresentação. |
| Lições aprendidas | registro autorizado. |
| Treinamentos | criação autorizada com participantes. |

## Regras comuns

- Escritas requerem o nível de acesso correspondente; leituras também são limitadas
  à empresa e, quando aplicável, ao vínculo do usuário com o ciclo.
- Não existem tools de SQL livre ou consulta MongoDB arbitrária.
- Predições retornam indisponibilidade quando não há dados ou variação suficientes;
  não inventam probabilidades.
- O RAG e a memória usam embeddings Gemini de 768 dimensões, mas em collections
  distintas: `acta_faq`, `memoria_mensagens` e `memoria_usuario` por padrão.

O resource `acta://catalog/tools` contém a descrição estruturada das tools disponíveis.
