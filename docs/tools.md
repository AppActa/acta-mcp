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
| Treinamentos | criação autorizada com participantes. |
| Lições aprendidas | criação baseada em evidências do ciclo com PDF/anexo, resumo e perguntas com referências. |
| FAQ | `faq_retriever` busca a documentação conceitual ACTA/PDCA com Qdrant semântico ou busca lexical local. |

## Regras comuns

- Escritas requerem o nível de acesso correspondente; leituras também são limitadas
  à empresa e, quando aplicável, ao vínculo do usuário com o ciclo.
- Não existem tools de SQL livre ou consulta MongoDB arbitrária.
- Predições retornam indisponibilidade quando não há dados ou variação suficientes;
  não inventam probabilidades.
- Memória de conversas e skills personalizadas são capacidades nativas do ACTA AI;
  não aparecem como tools MCP.

O resource `acta://catalog/tools` contém a descrição estruturada das tools disponíveis.
