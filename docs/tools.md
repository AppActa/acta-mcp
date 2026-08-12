# Catálogo de tools

## Ciclos

`ciclo_visao_geral`, `ciclo_problema_principal`, `ciclo_causas_raiz`, `ciclo_ishikawa`, `ciclo_riscos_pendencias`, `ciclo_treinamentos`, `ciclo_participantes`, `ciclo_relatorio_completo`, `ciclos_registrar_causa` e `ciclos_adicionar_item_ishikawa`.

## Tarefas

`tarefas_consultar`, `tarefas_atrasadas`, `tarefas_concluidas`, `tarefas_detalhes`, `tarefas_por_responsavel`, `tarefas_alertas_prazo`, `tarefas_relatorio_completo`, `tarefas_criar`, `tarefas_atualizar` e `tarefas_atualizar_status`.

As operações de escrita exigem `create`.

## Colaboradores

`colaboradores_consultar`, `colaborador_detalhes`, `colaboradores_participantes_ciclo`, `colaboradores_por_area`, `colaboradores_carga_trabalho`, `colaboradores_sugestao_realocacao` e `colaboradores_relatorio_completo`.

Dados pessoais como CPF, nascimento, telefone pessoal e e-mail adicional foram omitidos dos resultados. A empresa vem exclusivamente do contexto autenticado.

## RAG

`faq_retriever` usa busca vetorial semântica na collection Qdrant configurada. No startup, o MCP cria a collection quando necessário e sincroniza os documentos `ACTA_DOCS` por identificadores e hashes estáveis. Os embeddings são gerados pelo Qdrant Cloud Inference; o `acta-ai` não mantém mais um índice FAISS local.

## Formulários

`formularios_listar`, `formularios_detalhes`, `formularios_respostas`,
`formularios_resumo_respostas`, `formularios_criar_rascunho`,
`formularios_adicionar_pergunta` e `formularios_publicar` usam as collections MongoDB `formularios` e
`respostas_formulario`. Toda leitura é limitada ao ciclo e à empresa autenticada.
O resumo calcula campos mais respondidos e valores repetidos, mas não transforma
correlação ou frequência em causa raiz comprovada.

Todas as tools deste domínio exigem nível `geral`.

## Relatórios

`relatorios_contexto_ciclo` consolida os dados atuais de ciclo, tarefas, equipe e
formulários para o agente gerar o relatório sob demanda. Relatórios não são
persistidos em uma collection MongoDB. O contexto consolidado exige `geral`.

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

## Skills personalizadas

`skills_criar`, `skills_obter`, `skills_listar` e `skills_excluir` gerenciam skills
isoladas por `usuario_id` e `empresa_id`. Todas exigem somente `read`, porque a
skill pertence exclusivamente ao usuário autenticado.

O conteúdo aceito possui somente três seções: `# nome`, `# objetivo` e `# regras`.
Quando `# regras` não possui conteúdo, o valor salvo é `Nenhuma regra observada`.
O parser rejeita código, links, dados pessoais, prompt injection e referências a
agentes, especialistas, roteador, orquestrador, ferramentas ou tools. A skill é
revalidada sempre que for carregada, inclusive contra alterações diretas no MongoDB.
O índice único e todas as operações usam `empresa_id + usuario_id + slug`; skills não
são compartilhadas entre usuários, mesmo quando possuem o mesmo nome.

## Lições aprendidas e treinamentos

`licoes_aprendidas_registrar` persiste uma lição autorizada no MongoDB e exige
`create`. `treinamentos_criar` cria o treinamento e seus participantes em uma
transação PostgreSQL e exige `geral`.

## Resumo de autorização das criações

| Tools | Nível mínimo |
| --- | --- |
| `skills_*` | `read` |
| criações de tarefas/ciclos/lições | `create` |
| `formularios_*`, `treinamentos_criar` e contexto consolidado de relatório | `geral` |
| visão administrativa futura da empresa | `admin` |
