from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.modules.tarefas.schemas import TarefasQuery


class TarefasRepository:
    def __init__(self, postgres: PostgresRepository) -> None:
        self.postgres = postgres

    def consultar(self, query_input: TarefasQuery, empresa_id: int) -> list[dict]:
        query = """
            SELECT
                t.id, t.titulo, t.descricao, t.prioridade, t.status,
                t.data_inicio_real, t.data_fim_prevista, t.data_fim_real,
                t.criado_em, t.atualizado_em,
                CASE
                    WHEN t.data_fim_prevista < CURRENT_DATE
                         AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                    THEN TRUE ELSE FALSE
                END AS atrasada_calculada,
                pa.id AS id_plano_acao, pa.nome AS plano_acao,
                pa.objetivo AS objetivo_plano_acao, pa.status AS status_plano_acao,
                pa.prioridade AS prioridade_plano_acao, pa.origem AS origem_plano_acao,
                pa.id_ciclo,
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login AS email_responsavel, resp.tipo_usuario AS tipo_responsavel,
                resp.status AS status_usuario_responsavel,
                col_resp.id AS id_colaborador_responsavel,
                col_resp.cargo AS cargo_responsavel, col_resp.area AS area_responsavel,
                col_resp.status AS status_colaborador_responsavel
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp ON resp.id = t.id_responsavel
            LEFT JOIN colaborador col_resp ON col_resp.id_usuario = resp.id
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
        """
        params: list = [query_input.id_ciclo, empresa_id]
        if query_input.id_responsavel is not None:
            query += " AND t.id_responsavel = %s"
            params.append(query_input.id_responsavel)
        if query_input.status is not None:
            query += " AND t.status = %s"
            params.append(query_input.status)
        if query_input.prioridade is not None:
            query += " AND t.prioridade = %s"
            params.append(query_input.prioridade)
        if query_input.data_inicio is not None:
            query += " AND t.data_fim_prevista >= %s::date"
            params.append(query_input.data_inicio)
        if query_input.data_fim is not None:
            query += " AND t.data_fim_prevista <= %s::date"
            params.append(query_input.data_fim)
        if query_input.apenas_atrasadas:
            query += """
                AND (
                    t.status = 'ATRASADA'
                    OR (
                        t.data_fim_prevista < CURRENT_DATE
                        AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                    )
                )
            """
        query += """
            ORDER BY
                atrasada_calculada DESC,
                CASE t.prioridade
                    WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3 WHEN 'BAIXA' THEN 4 ELSE 5
                END,
                t.data_fim_prevista ASC, t.criado_em ASC
            LIMIT %s;
        """
        params.append(query_input.limit)
        return self.postgres.fetch_all(query, params)

    def detalhes(self, id_tarefa: int, empresa_id: int) -> dict | None:
        return self.postgres.fetch_one(
            """
            SELECT
                t.id, t.titulo, t.descricao, t.prioridade, t.status,
                t.data_inicio_real, t.data_fim_prevista, t.data_fim_real,
                t.criado_em, t.atualizado_em,
                CASE
                    WHEN t.data_fim_prevista < CURRENT_DATE
                         AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                    THEN TRUE ELSE FALSE
                END AS atrasada_calculada,
                pa.id AS id_plano_acao, pa.nome AS plano_acao,
                pa.objetivo AS objetivo_plano_acao, pa.status AS status_plano_acao,
                pa.prioridade AS prioridade_plano_acao, pa.origem AS origem_plano_acao,
                pa.id_ciclo,
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login AS email_responsavel, resp.tipo_usuario AS tipo_responsavel,
                resp.status AS status_usuario_responsavel,
                col_resp.id AS id_colaborador_responsavel,
                col_resp.cargo AS cargo_responsavel, col_resp.area AS area_responsavel,
                col_resp.status AS status_colaborador_responsavel
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp ON resp.id = t.id_responsavel
            LEFT JOIN colaborador col_resp ON col_resp.id_usuario = resp.id
            WHERE t.id = %s AND c.id_empresa = %s
            LIMIT 1;
            """,
            (id_tarefa, empresa_id),
        )

    def dependencias(self, id_tarefa: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                td.id_tarefa, td.id_tarefa_dependencia,
                dep.titulo AS tarefa_dependencia, dep.status AS status_dependencia,
                dep.prioridade AS prioridade_dependencia,
                dep.data_fim_prevista AS prazo_dependencia,
                resp_dep.id AS id_responsavel_dependencia,
                resp_dep.nome AS responsavel_dependencia
            FROM pdca.tarefa_dependencia td
            JOIN pdca.tarefa dep ON dep.id = td.id_tarefa_dependencia
            JOIN pdca.plano_acao pa ON pa.id = dep.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp_dep ON resp_dep.id = dep.id_responsavel
            WHERE td.id_tarefa = %s AND c.id_empresa = %s
            ORDER BY dep.data_fim_prevista ASC;
            """,
            (id_tarefa, empresa_id),
        )

    def bloqueia(self, id_tarefa: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                td.id_tarefa, td.id_tarefa_dependencia,
                t.titulo AS tarefa_bloqueada, t.status AS status_tarefa_bloqueada,
                t.prioridade AS prioridade_tarefa_bloqueada,
                t.data_fim_prevista AS prazo_tarefa_bloqueada,
                resp.id AS id_responsavel_tarefa_bloqueada,
                resp.nome AS responsavel_tarefa_bloqueada
            FROM pdca.tarefa_dependencia td
            JOIN pdca.tarefa t ON t.id = td.id_tarefa
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp ON resp.id = t.id_responsavel
            WHERE td.id_tarefa_dependencia = %s AND c.id_empresa = %s
            ORDER BY t.data_fim_prevista ASC;
            """,
            (id_tarefa, empresa_id),
        )

    def por_responsavel(
        self,
        id_ciclo: int,
        empresa_id: int,
        id_responsavel: int | None,
    ) -> list[dict]:
        query = """
            SELECT
                resp.id AS id_responsavel, resp.nome AS responsavel,
                resp.email_login, resp.tipo_usuario, resp.status AS status_usuario,
                col.id AS id_colaborador_responsavel, col.cargo, col.area,
                col.status AS status_colaborador,
                COUNT(t.id) AS total_tarefas,
                COUNT(*) FILTER (WHERE t.status = 'PENDENTE') AS pendentes,
                COUNT(*) FILTER (WHERE t.status = 'EM_ANDAMENTO') AS em_andamento,
                COUNT(*) FILTER (WHERE t.status = 'BLOQUEADA') AS bloqueadas,
                COUNT(*) FILTER (WHERE t.status = 'CONCLUIDA') AS concluidas,
                COUNT(*) FILTER (WHERE t.status = 'CANCELADA') AS canceladas,
                COUNT(*) FILTER (
                    WHERE t.status = 'ATRASADA'
                       OR (
                           t.data_fim_prevista < CURRENT_DATE
                           AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                       )
                ) AS atrasadas,
                COUNT(*) FILTER (WHERE t.prioridade = 'CRITICA') AS criticas,
                COUNT(*) FILTER (WHERE t.prioridade = 'ALTA') AS altas
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema resp ON resp.id = t.id_responsavel
            LEFT JOIN colaborador col ON col.id_usuario = resp.id
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
        """
        params: list[int] = [id_ciclo, empresa_id]
        if id_responsavel is not None:
            query += " AND resp.id = %s"
            params.append(id_responsavel)
        query += """
            GROUP BY resp.id, resp.nome, resp.email_login, resp.tipo_usuario,
                     resp.status, col.id, col.cargo, col.area, col.status
            ORDER BY atrasadas DESC, bloqueadas DESC, criticas DESC,
                     altas DESC, total_tarefas DESC, resp.nome ASC;
        """
        return self.postgres.fetch_all(query, params)

    def alertas(self, id_ciclo: int, empresa_id: int, somente_nao_lidos: bool) -> list[dict]:
        query = """
            SELECT
                a.id, a.mensagem, a.enviado_em, a.lido_em,
                t.id AS id_tarefa, t.titulo AS tarefa, t.status AS status_tarefa,
                t.prioridade AS prioridade_tarefa, t.data_fim_prevista,
                u.id AS id_usuario_destino, u.nome AS usuario_destino,
                u.email_login AS email_usuario_destino,
                u.tipo_usuario, u.status AS status_usuario_destino
            FROM pdca.alerta_prazo a
            JOIN pdca.tarefa t ON t.id = a.id_tarefa
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            JOIN usuario_sistema u ON u.id = a.id_usuario_destino
            WHERE pa.id_ciclo = %s AND c.id_empresa = %s
        """
        if somente_nao_lidos:
            query += " AND a.lido_em IS NULL"
        query += " ORDER BY a.lido_em NULLS FIRST, a.enviado_em DESC;"
        return self.postgres.fetch_all(query, (id_ciclo, empresa_id))
