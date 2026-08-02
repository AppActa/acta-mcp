from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository


class CiclosRepository:
    def __init__(self, postgres: PostgresRepository) -> None:
        self.postgres = postgres

    def visao_geral(self, id_ciclo: int, empresa_id: int) -> dict | None:
        return self.postgres.fetch_one(
            """
            SELECT
                c.id, c.titulo, c.descricao, c.status, c.data_inicio,
                c.data_estimada_fim, c.data_fim_real, c.id_ishikawa_mongo,
                c.criado_em, c.atualizado_em,
                e.id AS id_empresa, e.nome AS empresa,
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login AS email_responsavel,
                resp.tipo_usuario AS tipo_responsavel,
                resp.status AS status_responsavel,
                col.id AS id_colaborador_responsavel,
                col.cargo AS cargo_responsavel, col.area AS area_responsavel,
                COUNT(DISTINCT m.id) AS qnt_metas,
                COUNT(DISTINCT pa.id) AS qnt_planos_acao,
                COUNT(DISTINCT t.id) AS qnt_tarefas,
                COUNT(DISTINCT p.id) AS qnt_problemas,
                COUNT(DISTINCT cr.id) AS qnt_causas_raiz,
                COUNT(DISTINCT vr.id) AS qnt_verificacoes
            FROM pdca.ciclo c
            JOIN empresa e ON e.id = c.id_empresa
            JOIN usuario_sistema resp ON resp.id = c.id_responsavel
            LEFT JOIN colaborador col ON col.id_usuario = resp.id
            LEFT JOIN pdca.meta m ON m.id_ciclo = c.id
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = c.id
            LEFT JOIN pdca.tarefa t ON t.id_plano_acao = pa.id
            LEFT JOIN pdca.problema p ON p.id_ciclo = c.id
            LEFT JOIN pdca.causa_raiz cr ON cr.id_ciclo = c.id
            LEFT JOIN pdca.verificacao_resultado vr ON vr.id_ciclo = c.id
            WHERE c.id = %s AND c.id_empresa = %s
            GROUP BY c.id, e.id, e.nome, resp.id, resp.nome, resp.email_login,
                     resp.tipo_usuario, resp.status, col.id, col.cargo, col.area;
            """,
            (id_ciclo, empresa_id),
        )

    def tarefas_por_status(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT t.status, COUNT(*) AS quantidade
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
            GROUP BY t.status ORDER BY quantidade DESC;
            """,
            (id_ciclo, empresa_id),
        )

    def entity_status(
        self,
        table: str,
        id_ciclo: int,
        empresa_id: int,
    ) -> list[dict]:
        allowed_tables = {"meta", "plano_acao", "problema"}
        if table not in allowed_tables:
            raise ValueError("Tabela de status não autorizada.")
        return self.postgres.fetch_all(
            f"""
            SELECT entity.status, COUNT(*) AS quantidade
            FROM pdca.{table} entity
            JOIN pdca.ciclo c ON c.id = entity.id_ciclo
            WHERE entity.id_ciclo = %s AND c.id_empresa = %s
            GROUP BY entity.status ORDER BY quantidade DESC;
            """,
            (id_ciclo, empresa_id),
        )

    def problema_principal(self, id_ciclo: int, empresa_id: int) -> dict | None:
        return self.postgres.fetch_one(
            """
            SELECT
                p.id AS id_problema, p.titulo AS problema,
                p.descricao AS descricao_problema, p.peso,
                p.status AS status_problema, p.origem AS origem_problema,
                p.persistente, p.criado_em, p.atualizado_em,
                criador.id AS id_criador, criador.nome AS criado_por,
                cr.id AS id_causa_raiz, cr.descricao AS causa_raiz,
                cr.origem AS origem_causa_raiz, cr.aceita, cr.principal,
                cr.validada_em, cr.id_5_porques_mongo,
                validador.id AS id_validador, validador.nome AS validada_por,
                pa.id AS id_plano_acao, pa.nome AS plano_acao,
                pa.status AS status_plano_acao,
                pa.prioridade AS prioridade_plano_acao
            FROM pdca.problema p
            JOIN pdca.ciclo c ON c.id = p.id_ciclo
            JOIN usuario_sistema criador ON criador.id = p.criado_por
            LEFT JOIN LATERAL (
                SELECT inner_cr.*
                FROM pdca.causa_raiz inner_cr
                WHERE inner_cr.id_problema = p.id
                ORDER BY inner_cr.principal DESC, inner_cr.aceita DESC,
                         inner_cr.criado_em DESC
                LIMIT 1
            ) cr ON TRUE
            LEFT JOIN usuario_sistema validador ON validador.id = cr.validada_por
            LEFT JOIN pdca.plano_acao pa ON pa.id = cr.id_plano_acao
            WHERE p.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY p.peso DESC, p.persistente DESC, p.criado_em ASC
            LIMIT 1;
            """,
            (id_ciclo, empresa_id),
        )

    def causas_raiz(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                cr.id, cr.id_ciclo, cr.id_problema,
                p.titulo AS problema, p.status AS status_problema,
                p.peso AS peso_problema,
                cr.id_plano_acao, pa.nome AS plano_acao,
                pa.objetivo AS objetivo_plano, pa.prioridade AS prioridade_plano,
                pa.status AS status_plano, cr.id_5_porques_mongo,
                cr.descricao, cr.origem, cr.aceita, cr.principal,
                cr.validada_em, cr.criado_em, cr.atualizado_em,
                validador.id AS id_validador, validador.nome AS validada_por
            FROM pdca.causa_raiz cr
            JOIN pdca.ciclo c ON c.id = cr.id_ciclo
            JOIN pdca.problema p ON p.id = cr.id_problema
            LEFT JOIN pdca.plano_acao pa ON pa.id = cr.id_plano_acao
            LEFT JOIN usuario_sistema validador ON validador.id = cr.validada_por
            WHERE cr.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY cr.principal DESC, cr.aceita DESC,
                     p.peso DESC, cr.criado_em DESC;
            """,
            (id_ciclo, empresa_id),
        )

    def tarefas_em_risco(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                t.id, t.titulo, t.descricao, t.prioridade, t.status,
                t.data_inicio_real, t.data_fim_prevista, t.data_fim_real,
                CASE
                    WHEN t.data_fim_prevista < CURRENT_DATE
                         AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                    THEN TRUE ELSE FALSE
                END AS atrasada_calculada,
                pa.id AS id_plano_acao, pa.nome AS plano_acao,
                pa.status AS status_plano_acao,
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login AS email_responsavel,
                resp.tipo_usuario AS tipo_responsavel,
                col.id AS id_colaborador_responsavel,
                col.cargo AS cargo_responsavel, col.area AS area_responsavel
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp ON resp.id = t.id_responsavel
            LEFT JOIN colaborador col ON col.id_usuario = resp.id
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
              AND (
                  t.status IN ('PENDENTE', 'EM_ANDAMENTO', 'BLOQUEADA', 'ATRASADA')
                  OR (
                      t.data_fim_prevista < CURRENT_DATE
                      AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                  )
              )
            ORDER BY atrasada_calculada DESC,
                CASE t.prioridade
                    WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3 WHEN 'BAIXA' THEN 4 ELSE 5
                END,
                t.data_fim_prevista ASC;
            """,
            (id_ciclo, empresa_id),
        )

    def metas_em_risco(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                m.id, m.objetivo, m.valor_base, m.valor_alvo, m.unidade,
                m.prazo, m.status, m.prioridade, m.area, m.categoria,
                m.criado_em, m.atualizado_em,
                CASE
                    WHEN m.prazo < CURRENT_DATE
                         AND m.status NOT IN ('ATINGIDA', 'CANCELADA')
                    THEN TRUE ELSE FALSE
                END AS atrasada_calculada
            FROM pdca.meta m
            JOIN pdca.ciclo c ON c.id = m.id_ciclo
            WHERE m.id_ciclo = %s AND c.id_empresa = %s
              AND (
                  m.status IN (
                      'NAO_INICIADA', 'EM_ANDAMENTO',
                      'NAO_ATINGIDA', 'PARCIALMENTE_ATINGIDA'
                  )
                  OR (
                      m.prazo < CURRENT_DATE
                      AND m.status NOT IN ('ATINGIDA', 'CANCELADA')
                  )
              )
            ORDER BY atrasada_calculada DESC,
                CASE m.prioridade
                    WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3 WHEN 'BAIXA' THEN 4 ELSE 5
                END,
                m.prazo ASC;
            """,
            (id_ciclo, empresa_id),
        )

    def planos_problematicos(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                pa.id, pa.nome, pa.objetivo, pa.prioridade, pa.status,
                pa.origem, pa.criado_em, pa.atualizado_em,
                criador.id AS id_criador, criador.nome AS criado_por
            FROM pdca.plano_acao pa
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema criador ON criador.id = pa.criado_por
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
              AND pa.status IN ('RASCUNHO', 'EM_EXECUCAO', 'CANCELADO')
            ORDER BY
                CASE pa.prioridade
                    WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3 WHEN 'BAIXA' THEN 4 ELSE 5
                END,
                pa.criado_em ASC;
            """,
            (id_ciclo, empresa_id),
        )

    def alertas(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                a.id, a.mensagem, a.enviado_em, a.lido_em,
                t.id AS id_tarefa, t.titulo AS tarefa,
                t.status AS status_tarefa,
                u.id AS id_usuario_destino, u.nome AS usuario_destino,
                u.email_login, u.tipo_usuario
            FROM pdca.alerta_prazo a
            JOIN pdca.tarefa t ON t.id = a.id_tarefa
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema u ON u.id = a.id_usuario_destino
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY a.lido_em NULLS FIRST, a.enviado_em DESC;
            """,
            (id_ciclo, empresa_id),
        )

    def treinamentos(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                tr.id AS id_treinamento, tr.titulo, tr.descricao,
                tr.data_treinamento, tr.obrigatorio, tr.id_anexo_mongo,
                tr.criado_em, tr.atualizado_em,
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login AS email_responsavel,
                ut.id_usuario, usuario.nome AS usuario,
                usuario.email_login AS email_usuario, usuario.tipo_usuario,
                ut.obrigatorio AS obrigatorio_usuario,
                ut.status AS status_usuario_treinamento, ut.terminado_em,
                col.id AS id_colaborador, col.cargo, col.area
            FROM pdca.treinamento tr
            JOIN pdca.ciclo c ON c.id = tr.id_ciclo
            JOIN usuario_sistema resp ON resp.id = tr.id_responsavel
            LEFT JOIN pdca.usuario_treinamento ut ON ut.id_treinamento = tr.id
            LEFT JOIN usuario_sistema usuario ON usuario.id = ut.id_usuario
            LEFT JOIN colaborador col ON col.id_usuario = usuario.id
            WHERE tr.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY tr.data_treinamento ASC, tr.titulo ASC, usuario.nome ASC;
            """,
            (id_ciclo, empresa_id),
        )

    def participantes(self, id_ciclo: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                uc.id_ciclo, uc.id_usuario, uc.papel_ciclo,
                us.nome AS usuario, us.email_login, us.tipo_usuario,
                us.status AS status_usuario,
                col.id AS id_colaborador, col.cpf, col.cargo, col.area,
                col.permissao_gestor, col.status AS status_colaborador
            FROM pdca.usuario_ciclo uc
            JOIN pdca.ciclo c ON c.id = uc.id_ciclo
            JOIN usuario_sistema us ON us.id = uc.id_usuario
            LEFT JOIN colaborador col ON col.id_usuario = us.id
            WHERE uc.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY
                CASE uc.papel_ciclo
                    WHEN 'RESPONSAVEL' THEN 1 WHEN 'EXECUTOR' THEN 2
                    WHEN 'VALIDADOR' THEN 3 WHEN 'PARTICIPANTE' THEN 4
                    WHEN 'OBSERVADOR' THEN 5 ELSE 6
                END,
                us.nome ASC;
            """,
            (id_ciclo, empresa_id),
        )
