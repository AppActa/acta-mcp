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

## Predições

`predicoes_risco_atraso_tarefa`, `predicoes_estimativa_conclusao_tarefa`,
`predicoes_risco_atraso_ciclo`, `predicoes_estimativa_conclusao_ciclo`,
`predicoes_conclusao_treinamento`, `predicoes_sobrecarga_colaborador`,
`predicoes_atingimento_meta`, `predicoes_respostas_atipicas`,
`predicoes_tema_formulario` e `predicoes_recorrencia_problema` usam modelos
scikit-learn treinados apenas com dados históricos da empresa autenticada.

Classificações e regressões exigem amostras mínimas e variação do resultado. Quando
essas condições não são atendidas, a tool retorna `previsao_disponivel=false` em vez
de inventar uma probabilidade. Detecção de anomalias indica apenas respostas
estatisticamente incomuns; não comprova erro ou causa raiz.

## Memória

`memoria_garantir_sessao`, `memoria_salvar_mensagem`, `memoria_obter_contexto`,
`memoria_material_resumo`, `memoria_atualizar_resumo`, `memoria_registrar`,
`memoria_buscar`, `memoria_listar`, `memoria_excluir`,
`memoria_obter_consentimento` e `memoria_configurar_consentimento` implementam
memória persistente entre sessões.

MongoDB é a fonte oficial de sessões, mensagens, consentimentos e itens duráveis.
Qdrant é somente o índice de busca semântica. Toda operação usa simultaneamente
`usuario_id` e `empresa_id` do contexto autenticado. Mensagens expiram pelo TTL
configurado; itens explícitos permanecem até exclusão ou até a retenção escolhida
pelo usuário. Memórias inferidas exigem consentimento no modo `automatica`.
