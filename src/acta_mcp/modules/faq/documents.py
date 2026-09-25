"""
Base de conhecimento estática do Chatbot ACTA.

Este arquivo serve como fonte documental para dúvidas conceituais do ACTA.
Ele NÃO substitui consultas de informações atuais autorizadas.

Uso esperado:
- Explicar funcionalidades do ACTA.
- Responder dúvidas conceituais sobre PDCA, Ishikawa, 5 Porquês, 5W2H etc.
- Ajudar a identificar dúvidas conceituais.
- Servir como base inicial para embeddings/vetorização.

Perguntas sobre dados reais do ciclo, como:
- "Quais tarefas estão atrasadas?"
- "Quantos colaboradores participam deste ciclo?"
- "A meta foi atingida?"
- "Quem deve assumir essa tarefa?"

devem ser atendidas pelas funcionalidades autorizadas para dados atuais.
"""

ACTA_DOCS = [
    # =========================================================
    # INTRODUÇÃO E VISÃO GERAL
    # =========================================================
    {
        "id": "intro_acta",
        "title": "Introdução ao ACTA",
        "section": "Introdução",
        "phase": None,
        "audience": ["gestor", "colaborador"],
        "tags": ["acta", "pdca", "gestão", "projetos", "melhoria contínua"],
        "related_agents": ["rag"],
        "content": (
            "O ACTA é um sistema de gestão de projetos baseado na metodologia PDCA. "
            "Seu objetivo é centralizar todas as etapas do ciclo em um único ambiente, "
            "reduzindo burocracia, desperdícios, retrabalho e erros humanos. "
            "O sistema apoia a identificação, análise, execução, verificação e padronização "
            "de soluções para problemas organizacionais. Ele utiliza ferramentas como "
            "diagrama de Ishikawa, 5 Porquês, 5W2H, gráficos de Pareto, controle de prazos, "
            "dashboards comparativos, lições aprendidas e inteligência artificial."
        ),
        "example_questions": [
            "O que é o ACTA?",
            "Para que serve o ACTA?",
            "Qual é o objetivo do ACTA?",
        ],
    },
    {
        "id": "intro_pdca",
        "title": "Metodologia PDCA no ACTA",
        "section": "Introdução",
        "phase": None,
        "audience": ["gestor", "colaborador"],
        "tags": ["pdca", "plan", "do", "check", "act", "ciclo"],
        "related_agents": ["rag"],
        "content": (
            "O ACTA organiza o processo de melhoria contínua com base no ciclo PDCA: "
            "Plan, Do, Check e Act. Na fase Plan, o problema é identificado, analisado "
            "e planejado. Na fase Do, as ações são executadas. Na fase Check, os resultados "
            "são verificados e comparados com as metas. Na fase Act, o processo é padronizado, "
            "lições aprendidas são registradas e o ciclo pode ser encerrado ou reiniciado."
        ),
        "example_questions": [
            "Como funciona o PDCA no ACTA?",
            "Quais são as fases do ciclo?",
            "O que acontece em cada fase do PDCA?",
        ],
    },
    {
        "id": "intro_gestor",
        "title": "Panorama do Gestor",
        "section": "Introdução",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["gestor", "visão gerencial", "controle", "ciclo"],
        "related_agents": ["rag", "ciclo", "tarefas", "indicadores"],
        "content": (
            "O gestor possui acesso às informações autorizadas dos ciclos PDCA sob sua responsabilidade. "
            "Ele pode criar ciclos, definir metas, analisar problemas, validar causas raiz, criar planos "
            "de ação, acompanhar tarefas, verificar resultados, registrar efeitos secundários, aprovar lições "
            "aprendidas e gerar relatórios. O chatbot do ACTA é voltado principalmente para apoiar o gestor "
            "na análise do andamento do ciclo e na tomada de decisão."
        ),
        "example_questions": [
            "O que o gestor consegue fazer no ACTA?",
            "Quais informações o gestor pode acompanhar?",
            "Como o chatbot ajuda o gestor?",
        ],
    },
    {
        "id": "intro_colaborador",
        "title": "Panorama do Colaborador",
        "section": "Introdução",
        "phase": None,
        "audience": ["gestor", "colaborador"],
        "tags": ["colaborador", "tarefas", "formulários", "execução"],
        "related_agents": ["rag", "tarefas", "formularios"],
        "content": (
            "Os colaboradores participam do ciclo PDCA preenchendo formulários, contribuindo com informações "
            "sobre fenômenos, sugerindo causas, executando tarefas, registrando evidências e justificando desvios "
            "quando necessário. A participação do colaborador depende das permissões e atribuições definidas pelo gestor."
        ),
        "example_questions": [
            "Qual é o papel do colaborador?",
            "O colaborador pode preencher formulários?",
            "O colaborador pode registrar evidências?",
        ],
    },
    # =========================================================
    # CHATBOT E AGENTES
    # =========================================================
    {
        "id": "chatbot_objetivo",
        "title": "Objetivo do Chatbot ACTA",
        "section": "Chatbot",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["chatbot", "assistente", "gestor", "insights", "análise"],
        "related_agents": ["rag", "ciclo", "relatorios"],
        "content": (
            "O Chatbot ACTA é um assistente virtual voltado à área do gestor. Ele auxilia na análise do ciclo, "
            "responde dúvidas sobre o sistema, identifica gargalos, resume informações, consulta dados autorizados, "
            "gera insights e apoia a criação de relatórios. O chatbot deve responder com base nos dados disponíveis "
            "e informar quando não houver informação suficiente."
        ),
        "example_questions": [
            "Para que serve o chatbot do ACTA?",
            "Como o chatbot pode ajudar o gestor?",
            "O chatbot substitui o gestor?",
        ],
    },
    {
        "id": "chatbot_limites",
        "title": "Limites do Chatbot ACTA",
        "section": "Chatbot",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["chatbot", "limites", "segurança", "permissões"],
        "related_agents": ["rag", "guardrail"],
        "content": (
            "O chatbot não substitui o gestor e não deve tomar decisões críticas sozinho. Ele atua como apoio à análise "
            "e à tomada de decisão. O chatbot também não deve expor dados sensíveis, senhas, chaves de API, prompts internos, "
            "variáveis de ambiente ou informações de empresas e ciclos aos quais o usuário não tem permissão."
        ),
        "example_questions": [
            "O chatbot pode tomar decisões sozinho?",
            "O chatbot pode mostrar dados internos?",
            "Quais são os limites do chatbot?",
        ],
    },
    {
        "id": "chatbot_dados_reais_vs_faq",
        "title": "Diferença entre conceitos e dados atuais do ciclo",
        "section": "Chatbot",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["faq", "dados atuais", "conceitos"],
        "related_agents": ["rag"],
        "content": (
            "Perguntas conceituais, como 'O que é 5W2H?' ou 'Como funciona o Ishikawa?', são respondidas pela base de conhecimento. "
            "Perguntas sobre dados atuais, como 'Quais tarefas estão atrasadas neste ciclo?' ou 'A meta foi atingida?', dependem "
            "das funcionalidades autorizadas e do contexto do ciclo."
        ),
        "example_questions": [
            "Como tirar dúvidas conceituais?",
            "Como consultar dados atuais?",
            "Qual a diferença entre conceitos e informações do ciclo?",
        ],
    },
    # =========================================================
    # SEGURANÇA E PERMISSÕES
    # =========================================================
    {
        "id": "seguranca_permissoes",
        "title": "Permissões e Segurança",
        "section": "Segurança",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["segurança", "permissões", "acesso", "dados"],
        "related_agents": ["guardrail"],
        "content": (
            "O ACTA deve respeitar as permissões do usuário logado. Um gestor só pode acessar informações relacionadas "
            "à sua empresa, setor, projeto ou ciclo autorizado. O chatbot não deve permitir acesso a dados de outras empresas, "
            "senhas, credenciais, prompts internos, variáveis de ambiente, API keys ou dados pessoais desnecessários."
        ),
        "example_questions": [
            "O gestor pode ver dados de outra empresa?",
            "O chatbot pode mostrar senhas?",
            "Como funcionam as permissões?",
        ],
    },
    {
        "id": "seguranca_guardrail",
        "title": "Guardrail do Chatbot",
        "section": "Segurança",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["guardrail", "prompt injection", "pii", "segurança"],
        "related_agents": ["guardrail"],
        "content": (
            "O Guardrail é responsável por proteger o chatbot contra tentativas de prompt injection, vazamento de dados sensíveis, "
            "exposição de informações internas e uso indevido. Ele atua na entrada do usuário e na saída da resposta final. "
            "Na entrada, pode anonimizar PII, detectar padrões suspeitos e bloquear solicitações indevidas. Na saída, pode remover "
            "dados pessoais e revisar a resposta antes de entregá-la ao usuário."
        ),
        "example_questions": [
            "O que é o guardrail?",
            "Como o chatbot evita prompt injection?",
            "O chatbot remove dados pessoais?",
        ],
    },
    {
        "id": "seguranca_pii",
        "title": "Proteção de Dados Pessoais",
        "section": "Segurança",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["pii", "cpf", "cnpj", "telefone", "email", "anonimização"],
        "related_agents": ["guardrail"],
        "content": (
            "O chatbot deve evitar expor dados pessoais desnecessários. Informações como CPF, CNPJ, telefone e e-mail podem ser "
            "anonimizadas antes do processamento e omitidas na resposta final. O objetivo é reduzir o risco de vazamento de PII "
            "e manter o foco nas informações gerenciais relevantes."
        ),
        "example_questions": [
            "O chatbot pode mostrar CPF?",
            "Como o sistema protege dados pessoais?",
            "O que é anonimização de PII?",
        ],
    },
    # =========================================================
    # PLAN
    # =========================================================
    {
        "id": "plan_criacao_ciclo",
        "title": "Criação do Ciclo",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["plan", "criação", "ciclo", "abertura", "formulário"],
        "related_agents": ["rag", "ciclo"],
        "content": (
            "O gestor inicia um novo ciclo PDCA preenchendo um formulário de abertura. Esse formulário pode conter informações "
            "como título do ciclo, descrição do problema, setor envolvido, responsável, período de análise, indicador principal "
            "e contexto inicial. Após a validação dos dados, o sistema cria o ciclo e permite avançar para as próximas etapas do Plan."
        ),
        "example_questions": [
            "Como eu crio um novo ciclo?",
            "Quais informações são necessárias para abrir um ciclo?",
            "Quem pode criar um ciclo?",
        ],
    },
    {
        "id": "plan_identificacao_problema",
        "title": "Identificação do Problema",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["problema", "identificação", "indicador", "histórico", "plan"],
        "related_agents": ["rag", "indicadores", "ciclo"],
        "content": (
            "Na identificação do problema, o gestor registra o indicador principal e informa dados históricos para contextualizar "
            "a situação. Esses dados podem ser inseridos manualmente ou importados por arquivos CSV ou XLSX. Com base nas informações, "
            "o sistema pode gerar gráficos, apontar variações, sugerir problemas e apoiar a priorização do que deve ser investigado."
        ),
        "example_questions": [
            "Como identificar um problema no ACTA?",
            "Posso importar dados históricos?",
            "Como a IA ajuda a identificar problemas?",
        ],
    },
    {
        "id": "plan_importacao_dados",
        "title": "Importação de Dados Históricos",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["csv", "xlsx", "importação", "dados históricos", "indicadores"],
        "related_agents": ["rag", "indicadores"],
        "content": (
            "O ACTA permite que o gestor importe dados históricos por arquivos CSV ou XLSX. O sistema deve validar o formato do arquivo, "
            "mapear as colunas relevantes e transformar os dados em informações úteis para análise. Caso o arquivo seja inválido, o sistema "
            "deve exibir erro e permitir nova tentativa ou inserção manual."
        ),
        "example_questions": [
            "Posso importar um arquivo CSV?",
            "O ACTA aceita XLSX?",
            "O que acontece se o arquivo for inválido?",
        ],
    },
    {
        "id": "plan_analise_fenomeno",
        "title": "Análise de Fenômeno",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor", "colaborador"],
        "tags": ["fenômeno", "formulário", "ocorrência", "coleta", "plan"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "Na análise de fenômeno, o gestor configura formulários para coletar dados sobre as ocorrências do problema. "
            "Os colaboradores podem registrar sintomas, envolvidos, horário, localização, clima e campos personalizados. "
            "Esses dados ajudam a entender como, quando, onde e em quais condições o problema ocorre."
        ),
        "example_questions": [
            "O que é análise de fenômeno?",
            "Como os colaboradores registram ocorrências?",
            "Quais dados podem ser coletados no formulário?",
        ],
    },
    {
        "id": "plan_formularios_personalizados",
        "title": "Formulários Personalizados",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["formulários", "campos personalizados", "coleta"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "O gestor pode configurar formulários personalizados para coletar informações específicas do ciclo. Alguns campos podem ser "
            "predefinidos, como sintoma, colaborador envolvido, data, localização e clima. Outros campos podem ser criados pelo gestor. "
            "A flexibilidade permite adaptar a coleta às necessidades de cada ciclo."
        ),
        "example_questions": [
            "Posso criar campos personalizados?",
            "Quais campos existem nos formulários?",
            "Como funcionam os campos flexíveis dos formulários?",
        ],
    },
    {
        "id": "plan_gps_clima",
        "title": "Coleta Automática de Localização e Clima",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor", "colaborador"],
        "tags": ["gps", "clima", "api", "open-meteo", "fenômeno"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "Durante o preenchimento de formulários de fenômeno, o sistema pode capturar automaticamente informações como localização "
            "e clima. Esses dados ajudam a contextualizar a ocorrência e podem apoiar análises futuras, especialmente quando o problema "
            "tem relação com ambiente, horário, setor ou condições externas."
        ),
        "example_questions": [
            "O sistema captura localização?",
            "O clima entra na análise?",
            "Para que servem dados de GPS e clima?",
        ],
    },
    {
        "id": "plan_priorizacao_problemas",
        "title": "Priorização de Problemas",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor", "colaborador"],
        "tags": ["priorização", "problemas", "peso", "colaboradores", "drag and drop"],
        "related_agents": ["rag", "formularios", "indicadores"],
        "content": (
            "Após levantar problemas e subproblemas, o gestor pode definir pesos manualmente ou solicitar a priorização dos colaboradores. "
            "Nesse caso, os colaboradores podem ordenar problemas em um formulário, e o sistema calcula pesos com base nas respostas. "
            "O gestor pode aceitar os pesos sugeridos ou ajustá-los manualmente."
        ),
        "example_questions": [
            "Como priorizar problemas?",
            "Os colaboradores podem ajudar na priorização?",
            "O gestor pode alterar os pesos?",
        ],
    },
    {
        "id": "plan_ishikawa",
        "title": "Diagrama de Ishikawa",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor", "colaborador"],
        "tags": ["ishikawa", "6m", "causas", "espinha de peixe", "plan"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "O diagrama de Ishikawa, também conhecido como espinha de peixe, é usado para organizar possíveis causas de um problema. "
            "No ACTA, ele pode ser baseado nas categorias dos 6M: Máquina, Método, Mão de Obra, Meio Ambiente, Medidas e Matéria-Prima. "
            "Os colaboradores podem sugerir causas, e o gestor pode revisar, unificar, classificar e aprofundar a análise."
        ),
        "example_questions": [
            "Como funciona o diagrama de Ishikawa?",
            "O que são os 6M?",
            "Quem pode adicionar causas no Ishikawa?",
        ],
    },
    {
        "id": "plan_classificacao_hipoteses",
        "title": "Classificação de Hipóteses",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["hipóteses", "forte", "média", "fraca", "causas"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "Após levantar as possíveis causas, o gestor classifica cada hipótese como forte, média ou fraca. Hipóteses fortes são aquelas "
            "com maior evidência ou maior probabilidade de relação com o problema. Hipóteses médias têm relação possível, mas ainda incerta. "
            "Hipóteses fracas têm baixa evidência ou menor impacto aparente. O gestor pode registrar justificativas e anexar evidências."
        ),
        "example_questions": [
            "O que são hipóteses fortes?",
            "Qual a diferença entre hipótese média e fraca?",
            "Posso justificar uma classificação?",
        ],
    },
    {
        "id": "plan_cinco_porques",
        "title": "5 Porquês",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["5 porquês", "causa raiz", "hipóteses", "análise"],
        "related_agents": ["rag", "formularios"],
        "content": (
            "A técnica dos 5 Porquês é usada para aprofundar a análise de uma hipótese e chegar à causa raiz. "
            "No ACTA, hipóteses fortes devem passar obrigatoriamente por essa análise. O gestor também pode aplicar os 5 Porquês "
            "em hipóteses médias ou fracas quando considerar necessário. O resultado deve indicar uma ou mais causas raiz."
        ),
        "example_questions": [
            "Quando devo usar os 5 Porquês?",
            "Os 5 Porquês são obrigatórios?",
            "Como encontrar a causa raiz?",
        ],
    },
    {
        "id": "plan_causa_raiz",
        "title": "Causa Raiz",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["causa raiz", "problema", "bloqueio", "análise"],
        "related_agents": ["rag", "ciclo", "indicadores"],
        "content": (
            "A causa raiz é a origem principal do problema. Identificá-la corretamente é essencial para evitar soluções superficiais. "
            "No ACTA, a causa raiz pode ser registrada após análise de Ishikawa, classificação de hipóteses e aplicação dos 5 Porquês. "
            "A fase Check verificará se essa causa foi efetivamente bloqueada."
        ),
        "example_questions": [
            "O que é causa raiz?",
            "Como registrar uma causa raiz?",
            "Por que a causa raiz é importante?",
        ],
    },
    {
        "id": "plan_pareto",
        "title": "Gráfico de Pareto",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["pareto", "priorização", "80/20", "causas", "indicadores"],
        "related_agents": ["rag", "indicadores"],
        "content": (
            "O gráfico de Pareto ajuda o gestor a priorizar causas ou problemas com maior impacto. Ele organiza ocorrências por frequência "
            "ou relevância, permitindo identificar os fatores que mais contribuem para o problema. No ACTA, pode ser usado com dados como "
            "setor, data da ocorrência, problema identificado, causa raiz, quantidade de ocorrências e classificação da hipótese."
        ),
        "example_questions": [
            "Como funciona o gráfico de Pareto?",
            "Para que serve o Pareto?",
            "Como priorizar causas pelo Pareto?",
        ],
    },
    {
        "id": "plan_metas",
        "title": "Definição de Metas",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["metas", "objetivo", "indicador", "prazo", "responsáveis"],
        "related_agents": ["rag", "indicadores", "ciclo"],
        "content": (
            "As metas do ciclo devem ser definidas com clareza para permitir acompanhamento e verificação posterior. "
            "No ACTA, uma meta pode conter objetivo, valor-alvo mensurável, prazo estimado, responsáveis, tags, severidade, área e categoria. "
            "A meta deve estar ligada ao problema e ao indicador principal do ciclo."
        ),
        "example_questions": [
            "Como definir uma meta?",
            "Quais campos uma meta precisa ter?",
            "A meta precisa ser mensurável?",
        ],
    },
    {
        "id": "plan_5w2h",
        "title": "Plano de Ação 5W2H",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor", "colaborador"],
        "tags": ["5w2h", "plano de ação", "what", "why", "where", "who", "when", "how", "how much"],
        "related_agents": ["rag", "tarefas", "formularios"],
        "content": (
            "O 5W2H é uma ferramenta para estruturar planos de ação. Ele define: What, o que será feito; Why, por que será feito; "
            "Where, onde será feito; Who, quem será responsável; When, quando será feito; How, como será executado; e How much, quanto custará. "
            "No ACTA, o plano de ação pode ser criado pelo gestor, preenchido com apoio dos colaboradores ou sugerido pela IA."
        ),
        "example_questions": [
            "O que é 5W2H?",
            "Como criar um plano de ação?",
            "A IA pode sugerir ações corretivas?",
        ],
    },
    {
        "id": "plan_ia_acoes",
        "title": "Sugestões de Ações pela IA",
        "section": "Plan",
        "phase": "P",
        "audience": ["gestor"],
        "tags": ["ia", "ações corretivas", "5w2h", "sugestões"],
        "related_agents": ["rag", "relatorios"],
        "content": (
            "A IA pode sugerir ações corretivas com base nas causas raiz, no histórico do problema, nas respostas de formulários, "
            "nos dados do ciclo e em lições aprendidas anteriores. O gestor deve revisar as sugestões, podendo aceitar, editar, descartar "
            "ou criar ações manualmente."
        ),
        "example_questions": [
            "Como a IA sugere ações corretivas?",
            "O gestor pode editar sugestões da IA?",
            "A IA cria tarefas automaticamente?",
        ],
    },
    # =========================================================
    # DO
    # =========================================================
    {
        "id": "do_execucao_acoes",
        "title": "Execução das Ações",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["do", "execução", "ações", "tarefas", "colaboradores"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "Na fase Do, as ações planejadas são executadas. O gestor acompanha as tarefas atribuídas, responsáveis, prazos e status. "
            "Os colaboradores executam as tarefas, registram progresso, anexam evidências e justificam desvios quando a execução foge do plano 5W2H."
        ),
        "example_questions": [
            "O que acontece na fase Do?",
            "Como as ações são executadas?",
            "Quem registra a execução das tarefas?",
        ],
    },
    {
        "id": "do_tarefas",
        "title": "Tarefas Atribuídas",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["tarefas", "responsáveis", "prazo", "status"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "As tarefas são ações atribuídas a colaboradores dentro do ciclo. Elas podem conter responsável, prazo, descrição, relação com meta, "
            "status, evidências, observações e justificativas. Perguntas sobre tarefas reais do ciclo devem ser respondidas pelo agente de tarefas "
            "consultando os dados do sistema."
        ),
        "example_questions": [
            "Onde o gestor acompanha as tarefas?",
            "Como saber quem é responsável por uma tarefa?",
            "Quais status uma tarefa pode ter?",
        ],
    },
    {
        "id": "do_controle_prazos",
        "title": "Controle de Prazos",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor"],
        "tags": ["prazos", "atraso", "alerta", "tarefas", "notificação"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "O sistema monitora automaticamente os prazos das tarefas. Quando uma tarefa ultrapassa o prazo definido, o gestor pode receber "
            "um alerta. A partir disso, ele pode acompanhar a justificativa, reabrir a tarefa, definir novo prazo ou reatribuir a ação para outro colaborador."
        ),
        "example_questions": [
            "O que acontece quando uma tarefa atrasa?",
            "O gestor recebe alerta de atraso?",
            "Posso reabrir uma tarefa atrasada?",
        ],
    },
    {
        "id": "do_reatribuicao_tarefa",
        "title": "Reatribuição de Tarefas",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor"],
        "tags": ["reatribuição", "tarefas", "colaboradores", "competências"],
        "related_agents": ["rag", "tarefas", "colaboradores"],
        "content": (
            "O gestor pode reatribuir uma tarefa para outro colaborador quando houver atraso, indisponibilidade, mudança de prioridade ou melhor adequação "
            "de competência. A decisão pode considerar habilidades, setor, carga de trabalho, experiência e histórico de execução do colaborador."
        ),
        "example_questions": [
            "Como reatribuir uma tarefa?",
            "Quem pode assumir uma tarefa atrasada?",
            "O sistema considera competências na reatribuição?",
        ],
    },
    {
        "id": "do_treinamento",
        "title": "Treinamento dos Envolvidos",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["treinamento", "colaboradores", "tarefas", "requisito"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "Antes da execução de determinadas tarefas, o gestor pode registrar treinamentos obrigatórios ou opcionais para os colaboradores. "
            "O sistema pode armazenar data do treinamento, responsável, lista de presença digital e conteúdo ministrado. Dependendo da regra definida, "
            "o colaborador só acessa a tarefa após ter o treinamento registrado."
        ),
        "example_questions": [
            "Como funciona o treinamento no ACTA?",
            "O treinamento pode ser obrigatório?",
            "O colaborador precisa de treinamento para executar tarefa?",
        ],
    },
    {
        "id": "do_evidencias",
        "title": "Registro de Evidências",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["evidências", "anexos", "execução", "tarefas"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "Durante a execução das tarefas, os colaboradores podem registrar evidências como arquivos, observações, datas, imagens, documentos "
            "ou comentários. As evidências ajudam o gestor a validar se a ação foi executada corretamente e se houve aderência ao plano de ação."
        ),
        "example_questions": [
            "Posso anexar evidências?",
            "Que tipo de evidência pode ser registrada?",
            "Para que servem as evidências?",
        ],
    },
    {
        "id": "do_desvio_plano",
        "title": "Desvio do Plano de Ação",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["desvio", "justificativa", "5w2h", "execução"],
        "related_agents": ["rag", "tarefas", "formularios"],
        "content": (
            "Quando a execução de uma tarefa foge do plano de ação definido no 5W2H, o colaborador deve registrar uma justificativa. "
            "Essa justificativa permite ao gestor entender o motivo do desvio, avaliar impacto no ciclo e decidir se a tarefa deve ser ajustada, "
            "reaberta ou reatribuída."
        ),
        "example_questions": [
            "Como registrar um desvio do plano?",
            "Quando uma justificativa é obrigatória?",
            "O que acontece se a execução fugir do 5W2H?",
        ],
    },
    {
        "id": "do_painel_colaborador",
        "title": "Painel do Colaborador",
        "section": "Do",
        "phase": "D",
        "audience": ["gestor", "colaborador"],
        "tags": ["painel", "colaborador", "tarefas", "recados"],
        "related_agents": ["rag", "tarefas"],
        "content": (
            "O colaborador pode ter uma página pessoal com tarefas atribuídas, tarefas concluídas, recados do gestor, prazos e indicadores de participação. "
            "Pelo ponto de vista do gestor, essa visão ajuda a acompanhar a distribuição de trabalho e o progresso de cada colaborador."
        ),
        "example_questions": [
            "Onde o colaborador vê as tarefas?",
            "O gestor consegue acompanhar o painel do colaborador?",
            "O painel mostra recados do gestor?",
        ],
    },
    # =========================================================
    # CHECK
    # =========================================================
    {
        "id": "check_verificacao_resultados",
        "title": "Verificação de Resultados",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["check", "verificação", "resultados", "indicadores"],
        "related_agents": ["rag", "indicadores", "ciclo"],
        "content": (
            "Na fase Check, o gestor verifica se as ações executadas produziram os resultados esperados. O sistema compara os indicadores "
            "pós-execução com a linha de base inicial, avalia o atingimento das metas e ajuda a identificar se a causa raiz foi bloqueada."
        ),
        "example_questions": [
            "O que acontece na fase Check?",
            "Como verificar os resultados?",
            "Como comparar antes e depois?",
        ],
    },
    {
        "id": "check_dashboards",
        "title": "Dashboards de Comparação",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["dashboards", "indicadores", "antes e depois", "gráficos"],
        "related_agents": ["rag", "indicadores"],
        "content": (
            "Os dashboards do ACTA exibem comparações entre o cenário antes e depois da intervenção. Eles podem apresentar gráficos temporais, "
            "variação percentual, status da meta, tendências, padrões recorrentes e efeitos observados. A IA pode apoiar a leitura dos resultados "
            "e sugerir interpretações."
        ),
        "example_questions": [
            "Onde vejo os dashboards?",
            "Como funciona a comparação antes e depois?",
            "O sistema mostra variação percentual?",
        ],
    },
    {
        "id": "check_status_meta",
        "title": "Status de Atingimento da Meta",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["meta", "atingida", "parcial", "não atingida", "indicadores"],
        "related_agents": ["rag", "indicadores"],
        "content": (
            "O sistema pode classificar o resultado da meta como atingida, parcialmente atingida ou não atingida. Essa classificação depende "
            "da comparação entre o valor-alvo definido na fase Plan e o resultado obtido após a execução das ações na fase Do."
        ),
        "example_questions": [
            "Como saber se a meta foi atingida?",
            "O que significa meta parcialmente atingida?",
            "Como o ACTA calcula o status da meta?",
        ],
    },
    {
        "id": "check_validacao_causa_raiz",
        "title": "Validação da Causa Raiz",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["causa raiz", "bloqueio", "validação", "check"],
        "related_agents": ["rag", "indicadores", "ciclo"],
        "content": (
            "Na validação da causa raiz, o gestor registra se a causa identificada foi efetivamente bloqueada. Caso os resultados mostrem melhoria "
            "e a causa não volte a gerar o problema, o bloqueio pode ser considerado efetivo. Caso contrário, o sistema pode registrar o desvio "
            "e permitir retorno a etapas anteriores do PDCA."
        ),
        "example_questions": [
            "Como verificar se a causa raiz foi bloqueada?",
            "O que significa bloquear a causa raiz?",
            "O que acontece se a causa raiz não for bloqueada?",
        ],
    },
    {
        "id": "check_efeitos_secundarios",
        "title": "Efeitos Secundários",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["efeitos secundários", "positivos", "negativos", "check"],
        "related_agents": ["rag", "indicadores", "relatorios"],
        "content": (
            "Além dos resultados principais, o gestor pode registrar efeitos secundários observados após a implementação das ações. "
            "Esses efeitos podem ser positivos, como melhorias não previstas, ou negativos, como novos problemas gerados pela solução."
        ),
        "example_questions": [
            "Posso registrar efeitos colaterais?",
            "O que são efeitos secundários?",
            "Efeitos positivos também são registrados?",
        ],
    },
    {
        "id": "check_problema_nao_resolvido",
        "title": "Problema Não Resolvido",
        "section": "Check",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["problema não resolvido", "retorno", "desvio", "lições aprendidas"],
        "related_agents": ["rag", "ciclo"],
        "content": (
            "Caso o problema não seja resolvido ou a causa raiz não seja bloqueada, o ACTA deve registrar o desvio e preservar os dados "
            "no histórico de lições aprendidas. O gestor pode retornar para etapas anteriores, como análise de fenômeno, Ishikawa, 5 Porquês "
            "ou plano de ação, para revisar a investigação e propor novas ações."
        ),
        "example_questions": [
            "O que acontece se o problema não for resolvido?",
            "O ciclo volta para qual etapa?",
            "Os dados são perdidos se a solução falhar?",
        ],
    },
    # =========================================================
    # ACT
    # =========================================================
    {
        "id": "act_padronizacao",
        "title": "Padronização",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["act", "padronização", "pop", "it", "opl", "checklist"],
        "related_agents": ["rag", "relatorios"],
        "content": (
            "Quando a solução é validada, o gestor pode criar documentos de padronização para garantir que o novo processo continue sendo seguido. "
            "Esses documentos podem incluir POPs, instruções de trabalho, OPLs ou checklists. A padronização ajuda a manter os resultados obtidos."
        ),
        "example_questions": [
            "Como funciona a padronização?",
            "O que é POP?",
            "Quando criar um checklist?",
        ],
    },
    {
        "id": "act_comunicacao_padrao",
        "title": "Comunicação do Novo Padrão",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["comunicação", "novo padrão", "colaboradores", "evidência"],
        "related_agents": ["rag", "relatorios"],
        "content": (
            "Após criar um novo padrão, o gestor pode registrar a comunicação aos colaboradores. Essa comunicação pode conter destinatários, "
            "data, canal utilizado e evidências, como documentos PDF. O objetivo é comprovar que a equipe foi informada sobre o novo processo."
        ),
        "example_questions": [
            "Como comunicar um novo padrão?",
            "Posso anexar evidência da comunicação?",
            "Quem recebe o comunicado?",
        ],
    },
    {
        "id": "act_plano_auditoria",
        "title": "Plano de Auditoria",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["auditoria", "frequência", "responsável", "padronização"],
        "related_agents": ["rag", "relatorios"],
        "content": (
            "O plano de auditoria serve para acompanhar se o novo padrão continua sendo seguido após o encerramento do ciclo. "
            "Ele pode definir frequência da auditoria, responsável e data da primeira verificação. Auditorias ajudam a evitar que o problema retorne."
        ),
        "example_questions": [
            "Para que servem os planos de auditoria?",
            "Como criar um plano de auditoria?",
            "Quem é responsável pela auditoria?",
        ],
    },
    {
        "id": "act_licoes_aprendidas",
        "title": "Lições Aprendidas",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor", "colaborador"],
        "tags": ["lições aprendidas", "histórico", "aprendizado", "act"],
        "related_agents": ["rag"],
        "content": (
            "As lições aprendidas registram conhecimentos importantes obtidos durante o ciclo. Elas podem descrever o que funcionou, "
            "o que não funcionou, problemas que permaneceram, ações eficazes, causas recorrentes e recomendações para ciclos futuros. "
            "A IA pode sugerir lições aprendidas com base nos dados do ciclo."
        ),
        "example_questions": [
            "Onde ficam armazenadas as lições aprendidas?",
            "Quem pode registrar lições aprendidas?",
            "A IA sugere lições aprendidas?",
        ],
    },
    {
        "id": "act_historico_licoes",
        "title": "Histórico de Lições Aprendidas",
        "section": "Lições",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["histórico", "memória organizacional", "lições", "ciclos anteriores"],
        "related_agents": ["rag"],
        "content": (
            "O histórico de lições aprendidas funciona como uma memória organizacional. Ele permite consultar problemas anteriores, "
            "causas recorrentes, ações eficazes, soluções já utilizadas e recomendações para novos ciclos. Essa base ajuda a empresa "
            "a evitar repetição de erros e reutilizar conhecimento."
        ),
        "example_questions": [
            "Como consultar lições aprendidas de outros ciclos?",
            "Esse problema já aconteceu antes?",
            "O sistema guarda soluções antigas?",
        ],
    },
    {
        "id": "act_relatorio_one_click",
        "title": "Relatório One-Click",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["relatório", "pdf", "pptx", "one-click", "exportação"],
        "related_agents": ["rag", "relatorios"],
        "content": (
            "Ao final do ciclo, o ACTA pode gerar relatórios em PDF ou PPTX. O gestor pode selecionar fases do PDCA e incluir seções como "
            "introdução, problema redefinido, meta, causa raiz, plano de ação, verificação, padronização, lições aprendidas, dados adicionais, "
            "legendas, gráficos extras e texto livre."
        ),
        "example_questions": [
            "Como gerar o relatório final?",
            "Posso exportar em PPTX?",
            "Quais seções entram no relatório?",
        ],
    },
    {
        "id": "act_encerramento_ciclo",
        "title": "Encerramento do Ciclo",
        "section": "Act",
        "phase": "A",
        "audience": ["gestor"],
        "tags": ["encerramento", "ciclo", "relatório", "lições aprendidas"],
        "related_agents": ["rag", "ciclo", "relatorios"],
        "content": (
            "O ciclo pode ser encerrado após a verificação dos resultados, registro de lições aprendidas, padronização e geração do relatório final. "
            "Quando o problema não é resolvido, o ciclo pode retornar para etapas anteriores em vez de ser encerrado."
        ),
        "example_questions": [
            "Quando posso encerrar um ciclo?",
            "O que precisa acontecer antes de encerrar?",
            "O ciclo pode voltar para etapas anteriores?",
        ],
    },
    # =========================================================
    # INTELIGÊNCIA ARTIFICIAL
    # =========================================================
    {
        "id": "ia_funcao_geral",
        "title": "Inteligência Artificial no ACTA",
        "section": "IA",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["ia", "sugestões", "insights", "automação"],
        "related_agents": ["rag", "ciclo", "indicadores", "relatorios"],
        "content": (
            "A inteligência artificial no ACTA apoia diversas etapas do ciclo. Ela pode sugerir problemas, causas raiz, ações corretivas, "
            "priorizações, padrões recorrentes, riscos, melhorias e lições aprendidas. As sugestões da IA devem ser revisadas pelo gestor."
        ),
        "example_questions": [
            "Como a IA ajuda no ACTA?",
            "A IA toma decisões sozinha?",
            "Em quais etapas a IA atua?",
        ],
    },
    {
        "id": "ia_padroes_recorrentes",
        "title": "Identificação de Padrões Recorrentes",
        "section": "IA",
        "phase": "C",
        "audience": ["gestor"],
        "tags": ["ia", "padrões", "recorrência", "indicadores", "check"],
        "related_agents": ["indicadores"],
        "content": (
            "A IA pode apoiar a identificação de padrões recorrentes nos dados do ciclo, como causas mais comuns, ações mais eficazes, "
            "metas mais atingidas, setores com maior incidência de problemas e justificativas frequentes. Essa análise ajuda o gestor "
            "a tomar decisões com base em evidências."
        ),
        "example_questions": [
            "A IA consegue identificar padrões?",
            "Quais causas são mais comuns?",
            "Quais ações foram mais eficazes?",
        ],
    },
    {
        "id": "ia_resumo_executivo",
        "title": "Resumo Executivo com IA",
        "section": "IA",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["ia", "resumo", "relatório", "gestor", "diretoria"],
        "related_agents": ["relatorios"],
        "content": (
            "A IA pode gerar resumos executivos do ciclo para apoiar reuniões, apresentações e relatórios. Esses resumos podem incluir fase atual, "
            "principais problemas, metas, tarefas críticas, riscos, resultados, causa raiz, lições aprendidas e próximos passos."
        ),
        "example_questions": [
            "Gere um resumo executivo do ciclo",
            "Crie um resumo para reunião",
            "Quais são os principais pontos do ciclo?",
        ],
    },
    # =========================================================
    # COLABORADORES E CARGA DE TRABALHO
    # =========================================================
    {
        "id": "colaboradores_perfil_profissional",
        "title": "Perfil Profissional dos Colaboradores",
        "section": "Gestão",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["colaboradores", "cargo", "área", "realocação"],
        "related_agents": ["colaboradores", "tarefas"],
        "content": (
            "O ACTA consulta cargo, área, participação em ciclos e carga de tarefas dos colaboradores. "
            "Essas informações ajudam o gestor a avaliar atribuições e possíveis realocações, "
            "mas não substituem a validação de competências e disponibilidade com a equipe."
        ),
        "example_questions": [
            "Como consultar o perfil profissional dos colaboradores?",
            "Quem é mais indicado para uma tarefa?",
            "O sistema ajuda na realocação?",
        ],
    },
    {
        "id": "colaboradores_carga_trabalho",
        "title": "Carga de Trabalho dos Colaboradores",
        "section": "Gestão",
        "phase": "D",
        "audience": ["gestor"],
        "tags": ["carga de trabalho", "tarefas", "colaboradores", "disponibilidade"],
        "related_agents": ["colaboradores", "tarefas"],
        "content": (
            "O gestor deve considerar a carga de trabalho dos colaboradores ao atribuir novas tarefas. "
            "Cargo e área compatíveis não bastam quando a pessoa já possui muitas tarefas em andamento ou tarefas críticas em atraso."
        ),
        "example_questions": [
            "Quem está com mais tarefas?",
            "Quem aparenta ter menor carga de tarefas?",
            "Como escolher responsável por uma ação?",
        ],
    },
    # =========================================================
    # RELATÓRIOS E RESPOSTAS GERENCIAIS
    # =========================================================
    {
        "id": "relatorios_tipos",
        "title": "Tipos de Relatórios",
        "section": "Relatórios",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["relatórios", "resumo", "executivo", "pdf", "pptx"],
        "related_agents": ["relatorios"],
        "content": (
            "O chatbot pode apoiar a criação de diferentes tipos de relatórios, como resumo executivo, relatório da fase Plan, relatório da fase Do, "
            "relatório da fase Check, relatório da fase Act, relatório final do ciclo, roteiro para apresentação e texto para PDF ou PPTX."
        ),
        "example_questions": [
            "Gere um relatório do ciclo",
            "Crie um resumo executivo",
            "Monte um texto para apresentação",
        ],
    },
    {
        "id": "relatorios_linguagem_gestor",
        "title": "Linguagem das Respostas ao Gestor",
        "section": "Relatórios",
        "phase": None,
        "audience": ["gestor"],
        "tags": ["linguagem", "gestor", "resposta", "clareza"],
        "related_agents": ["relatorios", "juiz"],
        "content": (
            "As respostas do chatbot para o gestor devem ser claras, objetivas e orientadas à decisão. Sempre que possível, devem destacar situação atual, "
            "evidências, riscos, impacto e próximos passos. Quando não houver dados suficientes, o chatbot deve informar a limitação em vez de inventar."
        ),
        "example_questions": [
            "Como o chatbot deve responder ao gestor?",
            "O chatbot pode inventar dados?",
            "Como gerar uma resposta executiva?",
        ],
    },
]

