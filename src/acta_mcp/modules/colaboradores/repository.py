from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.modules.colaboradores.schemas import ColaboradoresQuery
from acta_mcp.modules.common import normalize_optional_text


class ColaboradoresRepository:
    def __init__(self, postgres: PostgresRepository) -> None:
        self.postgres = postgres

    def consultar(self, payload: ColaboradoresQuery, empresa_id: int) -> list[dict]:
        query = """
            SELECT
                col.id AS id_colaborador, col.nome AS colaborador,
                col.cargo, col.area, col.data_contratacao,
                col.permissao_gestor, col.status AS status_colaborador,
                col.criado_em AS colaborador_criado_em,
                col.atualizado_em AS colaborador_atualizado_em,
                us.id AS id_usuario, us.nome AS usuario,
                us.email_login, us.tipo_usuario, us.status AS status_usuario,
                emp.id AS id_empresa, emp.nome AS empresa,
                emp.tamanho_empresa, emp.setor_empresa,
                emp.status AS status_empresa
        """
        params: list = []
        if payload.id_ciclo is not None:
            query += ", uc.id_ciclo, uc.papel_ciclo"
        query += """
            FROM colaborador col
            JOIN usuario_sistema us ON us.id = col.id_usuario
            JOIN empresa emp ON emp.id = col.id_empresa
        """
        if payload.id_ciclo is not None:
            query += """
                JOIN pdca.usuario_ciclo uc
                  ON uc.id_usuario = us.id AND uc.id_ciclo = %s
                JOIN pdca.ciclo ciclo ON ciclo.id = uc.id_ciclo
            """
            params.append(payload.id_ciclo)
        query += " WHERE col.id_empresa = %s"
        params.append(empresa_id)
        if payload.id_ciclo is not None:
            query += " AND ciclo.id_empresa = %s"
            params.append(empresa_id)
        for field, value in (
            ("col.nome", normalize_optional_text(payload.nome)),
            ("col.area", normalize_optional_text(payload.area)),
            ("col.cargo", normalize_optional_text(payload.cargo)),
        ):
            if value is not None:
                query += f" AND {field} ILIKE %s"
                params.append(f"%{value}%")
        if payload.status is not None:
            query += " AND col.status = %s"
            params.append(payload.status)
        if payload.tipo_usuario is not None:
            query += " AND us.tipo_usuario = %s"
            params.append(payload.tipo_usuario)
        if payload.permissao_gestor is not None:
            query += " AND col.permissao_gestor = %s"
            params.append(payload.permissao_gestor)
        query += " ORDER BY col.status ASC, col.area ASC, col.nome ASC LIMIT %s;"
        params.append(payload.limit)
        return self.postgres.fetch_all(query, params)

    def detalhes(self, id_colaborador: int, empresa_id: int) -> dict | None:
        return self.postgres.fetch_one(
            """
            SELECT
                col.id AS id_colaborador, col.nome AS colaborador,
                col.cargo, col.area, col.data_contratacao,
                col.permissao_gestor, col.status AS status_colaborador,
                col.criado_em, col.atualizado_em,
                us.id AS id_usuario, us.nome AS usuario,
                us.email_login, us.tipo_usuario, us.status AS status_usuario,
                emp.id AS id_empresa, emp.nome AS empresa,
                emp.tamanho_empresa, emp.setor_empresa,
                emp.status AS status_empresa
            FROM colaborador col
            JOIN usuario_sistema us ON us.id = col.id_usuario
            JOIN empresa emp ON emp.id = col.id_empresa
            WHERE col.id = %s AND col.id_empresa = %s
            LIMIT 1;
            """,
            (id_colaborador, empresa_id),
        )

    def ciclos(self, id_usuario: int, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                uc.id_ciclo, uc.papel_ciclo, c.titulo AS ciclo,
                c.descricao AS descricao_ciclo, c.status AS status_ciclo,
                c.data_inicio, c.data_estimada_fim, c.data_fim_real
            FROM pdca.usuario_ciclo uc
            JOIN pdca.ciclo c ON c.id = uc.id_ciclo
            WHERE uc.id_usuario = %s AND c.id_empresa = %s
            ORDER BY c.data_inicio DESC, c.id DESC;
            """,
            (id_usuario, empresa_id),
        )

    def tarefas(
        self,
        id_usuario: int,
        empresa_id: int,
        id_ciclo: int | None,
    ) -> list[dict]:
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
                pa.status AS status_plano_acao,
                pa.prioridade AS prioridade_plano_acao, pa.id_ciclo
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            WHERE t.id_responsavel = %s AND c.id_empresa = %s
        """
        params: list[int] = [id_usuario, empresa_id]
        if id_ciclo is not None:
            query += " AND pa.id_ciclo = %s"
            params.append(id_ciclo)
        query += """
            ORDER BY atrasada_calculada DESC,
                CASE t.prioridade
                    WHEN 'CRITICA' THEN 1 WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3 WHEN 'BAIXA' THEN 4 ELSE 5
                END,
                t.data_fim_prevista ASC
            LIMIT 50;
        """
        return self.postgres.fetch_all(query, params)

    def participantes(self, id_ciclo: int, empresa_id: int, limit: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                uc.id_ciclo, uc.id_usuario, uc.papel_ciclo,
                us.nome AS usuario, us.email_login, us.tipo_usuario,
                us.status AS status_usuario,
                col.id AS id_colaborador, col.nome AS colaborador,
                col.cargo, col.area, col.data_contratacao,
                col.permissao_gestor, col.status AS status_colaborador,
                emp.id AS id_empresa, emp.nome AS empresa
            FROM pdca.usuario_ciclo uc
            JOIN pdca.ciclo c ON c.id = uc.id_ciclo
            JOIN usuario_sistema us ON us.id = uc.id_usuario
            LEFT JOIN colaborador col ON col.id_usuario = us.id
            LEFT JOIN empresa emp ON emp.id = us.id_empresa
            WHERE uc.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY
                CASE uc.papel_ciclo
                    WHEN 'RESPONSAVEL' THEN 1 WHEN 'EXECUTOR' THEN 2
                    WHEN 'VALIDADOR' THEN 3 WHEN 'PARTICIPANTE' THEN 4
                    WHEN 'OBSERVADOR' THEN 5 ELSE 6
                END,
                us.nome ASC
            LIMIT %s;
            """,
            (id_ciclo, empresa_id, limit),
        )

    def por_area(self, empresa_id: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                col.area, COUNT(*) AS total_colaboradores,
                COUNT(*) FILTER (WHERE col.status = 'ATIVO') AS ativos,
                COUNT(*) FILTER (WHERE col.status <> 'ATIVO') AS nao_ativos,
                COUNT(*) FILTER (WHERE col.permissao_gestor = TRUE) AS gestores,
                COUNT(*) FILTER (
                    WHERE us.tipo_usuario = 'GESTOR'
                ) AS usuarios_gestores
            FROM colaborador col
            JOIN usuario_sistema us ON us.id = col.id_usuario
            WHERE col.id_empresa = %s
            GROUP BY col.area
            ORDER BY total_colaboradores DESC, col.area ASC;
            """,
            (empresa_id,),
        )

    def carga_trabalho(self, id_ciclo: int, empresa_id: int, limit: int) -> list[dict]:
        return self.postgres.fetch_all(
            """
            SELECT
                us.id AS id_usuario, us.nome AS usuario,
                us.email_login, us.tipo_usuario, us.status AS status_usuario,
                uc.papel_ciclo, col.id AS id_colaborador,
                col.nome AS colaborador, col.cargo, col.area,
                col.status AS status_colaborador, col.permissao_gestor,
                COUNT(t.id) AS total_tarefas,
                COUNT(t.id) FILTER (WHERE t.status = 'PENDENTE') AS pendentes,
                COUNT(t.id) FILTER (WHERE t.status = 'EM_ANDAMENTO') AS em_andamento,
                COUNT(t.id) FILTER (WHERE t.status = 'BLOQUEADA') AS bloqueadas,
                COUNT(t.id) FILTER (WHERE t.status = 'CONCLUIDA') AS concluidas,
                COUNT(t.id) FILTER (WHERE t.status = 'CANCELADA') AS canceladas,
                COUNT(t.id) FILTER (
                    WHERE t.status = 'ATRASADA'
                       OR (
                           t.data_fim_prevista < CURRENT_DATE
                           AND t.status NOT IN ('CONCLUIDA', 'CANCELADA')
                       )
                ) AS atrasadas,
                COUNT(t.id) FILTER (WHERE t.prioridade = 'CRITICA') AS criticas,
                COUNT(t.id) FILTER (WHERE t.prioridade = 'ALTA') AS altas
            FROM pdca.usuario_ciclo uc
            JOIN pdca.ciclo c ON c.id = uc.id_ciclo
            JOIN usuario_sistema us ON us.id = uc.id_usuario
            LEFT JOIN colaborador col ON col.id_usuario = us.id
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = uc.id_ciclo
            LEFT JOIN pdca.tarefa t
              ON t.id_plano_acao = pa.id AND t.id_responsavel = us.id
            WHERE uc.id_ciclo = %s AND c.id_empresa = %s
            GROUP BY us.id, us.nome, us.email_login, us.tipo_usuario,
                     us.status, uc.papel_ciclo, col.id, col.nome,
                     col.cargo, col.area, col.status, col.permissao_gestor
            ORDER BY atrasadas DESC, bloqueadas DESC, criticas DESC,
                     altas DESC, total_tarefas DESC, us.nome ASC
            LIMIT %s;
            """,
            (id_ciclo, empresa_id, limit),
        )

    def candidatos_realocacao(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        area: str | None,
        cargo: str | None,
        limit: int,
    ) -> list[dict]:
        query = """
            SELECT
                us.id AS id_usuario, us.nome AS usuario,
                us.email_login, us.tipo_usuario, us.status AS status_usuario,
                col.id AS id_colaborador, col.nome AS colaborador,
                col.cargo, col.area, col.status AS status_colaborador,
                col.permissao_gestor, uc.papel_ciclo,
                COUNT(t.id) AS total_tarefas,
                COUNT(t.id) FILTER (
                    WHERE t.status IN ('PENDENTE','EM_ANDAMENTO','BLOQUEADA','ATRASADA')
                ) AS tarefas_abertas,
                COUNT(t.id) FILTER (WHERE t.status = 'BLOQUEADA') AS bloqueadas,
                COUNT(t.id) FILTER (
                    WHERE t.status = 'ATRASADA'
                       OR (
                           t.data_fim_prevista < CURRENT_DATE
                           AND t.status NOT IN ('CONCLUIDA','CANCELADA')
                       )
                ) AS atrasadas,
                COUNT(t.id) FILTER (WHERE t.prioridade = 'CRITICA') AS criticas,
                COUNT(t.id) FILTER (WHERE t.prioridade = 'ALTA') AS altas
            FROM colaborador col
            JOIN usuario_sistema us ON us.id = col.id_usuario
            LEFT JOIN pdca.usuario_ciclo uc
              ON uc.id_usuario = us.id AND uc.id_ciclo = %s
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = %s
            LEFT JOIN pdca.tarefa t
              ON t.id_plano_acao = pa.id AND t.id_responsavel = us.id
            WHERE col.status = 'ATIVO' AND us.status = 'ATIVO'
              AND col.id_empresa = %s AND us.id_empresa = %s
        """
        params: list = [id_ciclo, id_ciclo, empresa_id, empresa_id]
        if area is not None:
            query += " AND col.area ILIKE %s"
            params.append(f"%{area}%")
        if cargo is not None:
            query += " AND col.cargo ILIKE %s"
            params.append(f"%{cargo}%")
        query += """
            GROUP BY us.id, us.nome, us.email_login, us.tipo_usuario,
                     us.status, col.id, col.nome, col.cargo, col.area,
                     col.status, col.permissao_gestor, uc.papel_ciclo
            ORDER BY tarefas_abertas ASC, atrasadas ASC, bloqueadas ASC,
                     criticas ASC, altas ASC, total_tarefas ASC, col.nome ASC
            LIMIT %s;
        """
        params.append(limit)
        return self.postgres.fetch_all(query, params)

