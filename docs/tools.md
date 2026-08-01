# Catálogo de tools

## Ciclos

`ciclo_visao_geral`, `ciclo_problema_principal`, `ciclo_causas_raiz`, `ciclo_ishikawa`, `ciclo_riscos_pendencias`, `ciclo_treinamentos`, `ciclo_participantes`, `ciclo_relatorio_completo`.

## Tarefas

`tarefas_consultar`, `tarefas_atrasadas`, `tarefas_concluidas`, `tarefas_detalhes`, `tarefas_por_responsavel`, `tarefas_alertas_prazo`, `tarefas_justificativas`, `tarefas_relatorio_completo`.

## Colaboradores

`colaboradores_consultar`, `colaborador_detalhes`, `colaboradores_participantes_ciclo`, `colaboradores_por_area`, `colaboradores_carga_trabalho`, `colaboradores_competencias`, `colaboradores_disponibilidade`, `colaboradores_realocacoes`, `colaboradores_sugestao_realocacao`, `colaboradores_relatorio_completo`.

Dados pessoais como CPF, nascimento, telefone pessoal e e-mail adicional foram omitidos dos resultados. A empresa vem exclusivamente do contexto autenticado.

## RAG

`faq_retriever` usa busca vetorial semântica na collection Qdrant configurada. No startup, o MCP cria a collection quando necessário e sincroniza os documentos `ACTA_DOCS` por identificadores e hashes estáveis. Os embeddings são gerados pelo Qdrant Cloud Inference; o `acta-ai` não mantém mais um índice FAISS local.

## Formulários

`formularios_listar`, `formularios_detalhes`, `formularios_respostas` e
`formularios_resumo_respostas` leem as collections MongoDB `formularios` e
`respostas_formulario`. Toda leitura é limitada ao ciclo e à empresa autenticada.
O resumo calcula campos mais respondidos e valores repetidos, mas não transforma
correlação ou frequência em causa raiz comprovada.

## Relatórios

`relatorios_listar`, `relatorios_detalhes`, `relatorios_mais_recente` e
`relatorios_contexto_ciclo` são operações somente de leitura. Os três primeiros
consultam a collection MongoDB `relatorios`; o último consolida evidências atuais
de ciclos, tarefas, equipe e formulários para o agente produzir o texto.
