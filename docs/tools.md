# Catálogo de tools

As tools recebem apenas argumentos do domínio. Identidade, empresa, perfil e permissões
vêm do `RequestContext` autenticado e do PostgreSQL, nunca de argumentos escolhidos pelo
modelo.

| Domínio | Operações |
| --- | --- |
| Ciclos | Consultas de visão geral, problemas, Ishikawa, riscos, participantes e treinamentos; registro de causas e itens. |
| Tarefas | Consultas, atrasos, detalhes, responsáveis, alertas, relatórios, criação e edição. |
| Colaboradores | Consultas e detalhes vinculados ao ciclo, participação, carga e sugestão de realocação; `colaboradores_por_area` é empresarial. |
| Formulários | Leitura de formulários e respostas, criação de rascunhos, perguntas e publicação. |
| Relatórios | Contexto consolidado de um ciclo para geração pelo ACTA AI. |
| Treinamentos | Criação de treinamento e vinculação de participantes. |
| Lições aprendidas | Criação baseada em evidências do ciclo com PDF/anexo, resumo e perguntas com referências. |
| FAQ | `faq_retriever` pesquisa documentação conceitual do ACTA/PDCA usando Qdrant ou busca lexical local. |

## Escopo e autorização

- Cada tool que lê ou altera dados de ciclo recebe um `id_ciclo` inteiro obrigatório e
  confirma esse ciclo no PostgreSQL antes de acessar seus dados.
- As tools de tarefa por `id_tarefa` também recebem o `id_ciclo`; a tarefa deve pertencer
  exatamente ao ciclo informado.
- Consultas de colaboradores, detalhes e resumo de lições não aceitam ciclo ausente e
  não ampliam a busca para todos os dados da empresa.
- O perfil `GESTOR` pode criar e editar dados apenas em ciclos aos quais está vinculado.
  Outros perfis vinculados e `ADMIN` podem somente ler. `ADMIN` pode ler ciclos da própria
  empresa sem vínculo individual. Exclusão de dados de ciclo é negada.
- Leituras de formulários, respostas e contexto de relatório estão disponíveis para
  perfis com acesso de leitura ao ciclo.
- Operações genuinamente empresariais sem dados de ciclo, como `colaboradores_por_area`,
  continuam limitadas à empresa autenticada.
- Não existem tools de SQL livre ou consulta MongoDB arbitrária.
- Memória de conversas e skills personalizadas são capacidades nativas do ACTA AI; não
  aparecem como tools MCP.

O resource `acta://catalog/tools` contém a descrição estruturada das tools disponíveis.
