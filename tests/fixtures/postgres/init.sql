CREATE SCHEMA IF NOT EXISTS pdca;

CREATE TABLE empresa (
    id BIGINT PRIMARY KEY,
    nome TEXT NOT NULL,
    tamanho_empresa TEXT,
    setor_empresa TEXT,
    status TEXT NOT NULL
);

CREATE TABLE usuario_sistema (
    id BIGINT PRIMARY KEY,
    id_empresa BIGINT NOT NULL REFERENCES empresa(id),
    nome TEXT NOT NULL,
    email_login TEXT NOT NULL,
    tipo_usuario TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE colaborador (
    id BIGINT PRIMARY KEY,
    id_usuario BIGINT NOT NULL REFERENCES usuario_sistema(id),
    id_empresa BIGINT NOT NULL REFERENCES empresa(id),
    nome TEXT NOT NULL,
    cpf TEXT,
    cargo TEXT,
    area TEXT,
    data_nascimento DATE,
    data_contratacao DATE,
    permissao_gestor BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.ciclo (
    id BIGINT PRIMARY KEY,
    id_empresa BIGINT NOT NULL REFERENCES empresa(id),
    id_responsavel BIGINT NOT NULL REFERENCES usuario_sistema(id),
    titulo TEXT NOT NULL,
    descricao TEXT,
    status TEXT NOT NULL,
    data_inicio DATE,
    data_estimada_fim DATE,
    data_fim_real DATE,
    id_ishikawa_mongo TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.meta (
    id BIGINT PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    objetivo TEXT NOT NULL,
    valor_base NUMERIC,
    valor_alvo NUMERIC,
    unidade TEXT,
    prazo DATE,
    status TEXT NOT NULL,
    prioridade TEXT NOT NULL,
    area TEXT,
    categoria TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.plano_acao (
    id BIGINT PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    criado_por BIGINT NOT NULL REFERENCES usuario_sistema(id),
    nome TEXT NOT NULL,
    objetivo TEXT,
    prioridade TEXT NOT NULL,
    status TEXT NOT NULL,
    origem TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.tarefa (
    id BIGSERIAL PRIMARY KEY,
    id_plano_acao BIGINT NOT NULL REFERENCES pdca.plano_acao(id),
    id_responsavel BIGINT NOT NULL REFERENCES usuario_sistema(id),
    titulo TEXT NOT NULL,
    descricao TEXT,
    prioridade TEXT NOT NULL,
    status TEXT NOT NULL,
    data_inicio_real DATE,
    data_fim_prevista DATE,
    data_fim_real DATE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.problema (
    id BIGINT PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    criado_por BIGINT NOT NULL REFERENCES usuario_sistema(id),
    titulo TEXT NOT NULL,
    descricao TEXT,
    peso NUMERIC,
    status TEXT NOT NULL,
    origem TEXT,
    persistente BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.causa_raiz (
    id BIGSERIAL PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    id_problema BIGINT NOT NULL REFERENCES pdca.problema(id),
    id_plano_acao BIGINT REFERENCES pdca.plano_acao(id),
    id_5_porques_mongo TEXT,
    descricao TEXT NOT NULL,
    origem TEXT,
    aceita BOOLEAN NOT NULL DEFAULT FALSE,
    principal BOOLEAN NOT NULL DEFAULT FALSE,
    validada_em TIMESTAMPTZ,
    validada_por BIGINT REFERENCES usuario_sistema(id),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.verificacao_resultado (
    id BIGINT PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id)
);

CREATE TABLE pdca.alerta_prazo (
    id BIGINT PRIMARY KEY,
    id_tarefa BIGINT NOT NULL REFERENCES pdca.tarefa(id),
    id_usuario_destino BIGINT NOT NULL REFERENCES usuario_sistema(id),
    mensagem TEXT NOT NULL,
    enviado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lido_em TIMESTAMPTZ
);

CREATE TABLE pdca.treinamento (
    id BIGSERIAL PRIMARY KEY,
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    id_responsavel BIGINT NOT NULL REFERENCES usuario_sistema(id),
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_treinamento DATE,
    obrigatorio BOOLEAN NOT NULL DEFAULT FALSE,
    id_anexo_mongo TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pdca.usuario_treinamento (
    id_treinamento BIGINT NOT NULL REFERENCES pdca.treinamento(id),
    id_usuario BIGINT NOT NULL REFERENCES usuario_sistema(id),
    obrigatorio BOOLEAN NOT NULL DEFAULT FALSE,
    status TEXT NOT NULL,
    terminado_em TIMESTAMPTZ,
    PRIMARY KEY (id_treinamento, id_usuario)
);

CREATE TABLE pdca.usuario_ciclo (
    id_ciclo BIGINT NOT NULL REFERENCES pdca.ciclo(id),
    id_usuario BIGINT NOT NULL REFERENCES usuario_sistema(id),
    papel_ciclo TEXT NOT NULL,
    PRIMARY KEY (id_ciclo, id_usuario)
);

CREATE TABLE pdca.tarefa_dependencia (
    id_tarefa BIGINT NOT NULL REFERENCES pdca.tarefa(id),
    id_tarefa_dependencia BIGINT NOT NULL REFERENCES pdca.tarefa(id),
    PRIMARY KEY (id_tarefa, id_tarefa_dependencia)
);

INSERT INTO empresa VALUES
    (1, 'ACTA Teste', 'MEDIA', 'Tecnologia', 'ATIVO'),
    (2, 'Outra Empresa', 'PEQUENA', 'Serviços', 'ATIVO');

INSERT INTO usuario_sistema VALUES
    (1, 1, 'Ana Gestora', 'ana@acta.local', 'GESTOR', 'ATIVO'),
    (2, 1, 'Bruno Analista', 'bruno@acta.local', 'COLABORADOR', 'ATIVO'),
    (3, 1, 'Carla Operações', 'carla@acta.local', 'COLABORADOR', 'ATIVO'),
    (20, 2, 'Usuário Externo', 'externo@outra.local', 'GESTOR', 'ATIVO');

INSERT INTO colaborador (
    id, id_usuario, id_empresa, nome, cpf, cargo, area,
    data_nascimento, data_contratacao, permissao_gestor, status
) VALUES
    (1, 1, 1, 'Ana Gestora', '00000000000', 'Gerente', 'Qualidade',
     DATE '1985-01-01', DATE '2020-01-10', TRUE, 'ATIVO'),
    (2, 2, 1, 'Bruno Analista', '11111111111', 'Analista', 'Qualidade',
     DATE '1990-02-02', DATE '2021-03-15', FALSE, 'ATIVO'),
    (3, 3, 1, 'Carla Operações', '22222222222', 'Supervisora', 'Operações',
     DATE '1992-03-03', DATE '2022-04-20', FALSE, 'ATIVO'),
    (20, 20, 2, 'Usuário Externo', '99999999999', 'Gerente', 'Externo',
     DATE '1980-01-01', DATE '2019-01-01', TRUE, 'ATIVO');

INSERT INTO pdca.ciclo (
    id, id_empresa, id_responsavel, titulo, descricao, status,
    data_inicio, data_estimada_fim, id_ishikawa_mongo
) VALUES
    (1, 1, 1, 'Reduzir retrabalho', 'Ciclo de melhoria operacional', 'DO',
     CURRENT_DATE - 30, CURRENT_DATE + 30, 'ishikawa-1'),
    (2, 2, 20, 'Ciclo confidencial', 'Dados de outro tenant', 'PLAN',
     CURRENT_DATE - 10, CURRENT_DATE + 60, 'ishikawa-2');

INSERT INTO pdca.meta VALUES
    (1, 1, 'Reduzir retrabalho em 20%', 100, 80, '%', CURRENT_DATE - 1,
     'EM_ANDAMENTO', 'ALTA', 'Operações', 'Qualidade', NOW(), NOW());

INSERT INTO pdca.plano_acao VALUES
    (1, 1, 1, 'Padronizar processo', 'Reduzir variação', 'ALTA',
     'EM_EXECUCAO', 'ISHIKAWA', NOW(), NOW()),
    (2, 2, 20, 'Plano externo', 'Confidencial', 'ALTA',
     'EM_EXECUCAO', 'MANUAL', NOW(), NOW());

INSERT INTO pdca.tarefa VALUES
    (1, 1, 2, 'Mapear processo', 'Documentar fluxo atual', 'ALTA',
     'EM_ANDAMENTO', CURRENT_DATE - 20, CURRENT_DATE - 2, NULL, NOW(), NOW()),
    (2, 1, 3, 'Validar padrão', 'Validar com operação', 'CRITICA',
     'BLOQUEADA', CURRENT_DATE - 10, CURRENT_DATE + 5, NULL, NOW(), NOW()),
    (3, 1, 2, 'Treinar equipe', 'Executar treinamento', 'MEDIA',
     'CONCLUIDA', CURRENT_DATE - 15, CURRENT_DATE - 5, CURRENT_DATE - 6, NOW(), NOW()),
    (20, 2, 20, 'Tarefa externa', 'Confidencial', 'ALTA',
     'PENDENTE', CURRENT_DATE, CURRENT_DATE + 10, NULL, NOW(), NOW());

INSERT INTO pdca.problema VALUES
    (1, 1, 1, 'Retrabalho alto', 'Variação na execução', 10, 'ANALISADO',
     'INTERNA', TRUE, NOW(), NOW());

INSERT INTO pdca.causa_raiz VALUES
    (1, 1, 1, 1, 'cinco-porques-1', 'Ausência de padrão operacional',
     'ISHIKAWA', TRUE, TRUE, NOW(), 1, NOW(), NOW());

INSERT INTO pdca.verificacao_resultado VALUES (1, 1);

INSERT INTO pdca.alerta_prazo VALUES
    (1, 1, 2, 'A tarefa Mapear processo está atrasada.', NOW(), NULL);

INSERT INTO pdca.treinamento VALUES
    (1, 1, 1, 'Padrão operacional', 'Treinamento do novo fluxo',
     CURRENT_DATE + 3, TRUE, 'anexo-1', NOW(), NOW());

INSERT INTO pdca.usuario_treinamento VALUES
    (1, 2, TRUE, 'PENDENTE', NULL),
    (1, 3, TRUE, 'CONCLUIDO', NOW());

INSERT INTO pdca.usuario_ciclo VALUES
    (1, 1, 'RESPONSAVEL'),
    (1, 2, 'EXECUTOR'),
    (1, 3, 'VALIDADOR'),
    (2, 20, 'RESPONSAVEL');

INSERT INTO pdca.tarefa_dependencia VALUES (2, 1);

SELECT setval(pg_get_serial_sequence('pdca.tarefa', 'id'), (SELECT MAX(id) FROM pdca.tarefa));
SELECT setval(
    pg_get_serial_sequence('pdca.causa_raiz', 'id'),
    (SELECT MAX(id) FROM pdca.causa_raiz)
);
SELECT setval(
    pg_get_serial_sequence('pdca.treinamento', 'id'),
    (SELECT MAX(id) FROM pdca.treinamento)
);
