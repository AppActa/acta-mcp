# Catálogo de tools

As tools recebem apenas argumentos do domínio. Identidade, empresa, perfil e permissões
vêm do `RequestContext` autenticado e do PostgreSQL, nunca de argumentos escolhidos pelo
modelo.

| Domínio | Operações |
| --- | --- |
| Ciclos | Busca de ciclos acessíveis por título ou descrição; consultas de visão geral, problemas, Ishikawa, riscos, participantes e treinamentos; registro de causas e itens. |
| Tarefas | Consultas por ciclo, resumo total entre ciclos autorizados, consulta limitada entre ciclos, atrasos, detalhes, responsáveis, alertas, relatórios, criação e edição. |
| Colaboradores | Consultas e detalhes vinculados ao ciclo, participação, carga e sugestão de realocação; `colaboradores_por_area` é empresarial. |
| Formulários | Leitura de formulários e respostas, criação de rascunhos, perguntas e publicação. |
| Relatórios | Contexto consolidado de um ciclo para geração pelo ACTA AI. |
| Treinamentos | Criação de treinamento e vinculação de participantes. |
| Lições aprendidas | Criação baseada em evidências do ciclo com PDF/anexo, listagem, resumo e perguntas por ciclo ou entre ciclos autorizados com referências. |
| FAQ | `faq_retriever` pesquisa documentação conceitual do ACTA/PDCA usando Qdrant ou busca lexical local. |

## Escopo e autorização

- `ciclos_buscar_por_descricao` pesquisa título e descrição somente nos ciclos aos quais
  o usuário autenticado tem acesso; ela retorna metadados para ajudar a identificar o ciclo.
- Cada tool que lê ou altera dados de um ciclo específico recebe um `id_ciclo` inteiro
  obrigatório e confirma esse ciclo no PostgreSQL antes de acessar seus dados.
- As tools de tarefa por `id_tarefa` também recebem o `id_ciclo`; a tarefa deve pertencer
  exatamente ao ciclo informado.
- As tools `tarefas_resumo_entre_ciclos`, `tarefas_consultar_entre_ciclos`,
  `licoes_listar_entre_ciclos`, `licoes_resumir_entre_ciclos` e
  `licoes_perguntar_entre_ciclos` são leituras explícitas entre ciclos. O servidor deriva
  a lista de ciclos autorizados do usuário autenticado; nenhum argumento do modelo define
  empresa ou ciclos. Listas têm limite máximo e cada tarefa/lição inclui `id_ciclo`.
- As tools de consultas por ciclo continuam exigindo `id_ciclo`; consultas de colaboradores,
  detalhes e demais dados não ampliam a busca para todos os ciclos da empresa.
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
