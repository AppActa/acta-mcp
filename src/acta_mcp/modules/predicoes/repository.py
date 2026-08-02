from typing import Any

from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.infrastructure.serializers import serialize


def _mongo_scope(prefix: str, identifier: int | str) -> dict[str, Any]:
    text = str(identifier)
    variants: list[Any] = [identifier, text]
    if text.isdigit():
        variants.append(int(text))
    title = prefix.title().replace("_", "")
    return {
        "$or": [
            {f"id_{prefix}": {"$in": variants}},
            {f"{prefix}_id": {"$in": variants}},
            {f"id{title}": {"$in": variants}},
            {f"{prefix.split('_')[0]}Id": {"$in": variants}},
        ]
    }


class PredicoesRepository:
    def __init__(self, postgres: PostgresRepository, mongo: MongoRepository) -> None:
        self.postgres = postgres
        self.database = mongo.database

    def task_training(self, empresa_id: int) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT t.id, t.prioridade,
                   GREATEST(t.data_fim_prevista - COALESCE(t.data_inicio_real, t.criado_em::date), 0)
                       AS prazo_planejado_dias,
                   COUNT(DISTINCT td.id_tarefa_dependencia) AS dependencias,
                   EXTRACT(DOW FROM t.criado_em)::int AS dia_semana_criacao,
                   CASE WHEN t.data_fim_real > t.data_fim_prevista
                              OR t.status = 'ATRASADA' THEN 1 ELSE 0 END AS alvo_atraso,
                   GREATEST(t.data_fim_real - COALESCE(t.data_inicio_real, t.criado_em::date), 0)
                       AS duracao_real_dias,
                   t.criado_em
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            LEFT JOIN pdca.tarefa_dependencia td ON td.id_tarefa = t.id
            WHERE c.id_empresa = %s AND t.data_fim_real IS NOT NULL
              AND t.status <> 'CANCELADA'
            GROUP BY t.id
            ORDER BY t.criado_em, t.id;
            """,
            (empresa_id,),
        )

    def task_current(self, id_tarefa: int, empresa_id: int) -> dict[str, Any] | None:
        return self.postgres.fetch_one(
            """
            SELECT t.id, t.titulo, t.prioridade, t.status,
                   COALESCE(t.data_inicio_real, t.criado_em::date) AS data_base,
                   t.data_fim_prevista,
                   GREATEST(t.data_fim_prevista - COALESCE(t.data_inicio_real, t.criado_em::date), 0)
                       AS prazo_planejado_dias,
                   COUNT(DISTINCT td.id_tarefa_dependencia) AS dependencias,
                   EXTRACT(DOW FROM t.criado_em)::int AS dia_semana_criacao
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            LEFT JOIN pdca.tarefa_dependencia td ON td.id_tarefa = t.id
            WHERE t.id = %s AND c.id_empresa = %s
            GROUP BY t.id;
            """,
            (id_tarefa, empresa_id),
        )

    def cycle_training(self, empresa_id: int) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT c.id,
                   GREATEST(c.data_estimada_fim - c.data_inicio, 0) AS prazo_planejado_dias,
                   COUNT(DISTINCT pa.id) AS planos,
                   COUNT(DISTINCT t.id) AS tarefas,
                   COUNT(DISTINCT m.id) AS metas,
                   COUNT(DISTINCT p.id) AS problemas,
                   COUNT(DISTINCT uc.id_usuario) AS participantes,
                   CASE WHEN c.data_fim_real > c.data_estimada_fim THEN 1 ELSE 0 END
                       AS alvo_atraso,
                   GREATEST(c.data_fim_real - c.data_inicio, 0) AS duracao_real_dias,
                   c.criado_em
            FROM pdca.ciclo c
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = c.id
            LEFT JOIN pdca.tarefa t ON t.id_plano_acao = pa.id
            LEFT JOIN pdca.meta m ON m.id_ciclo = c.id
            LEFT JOIN pdca.problema p ON p.id_ciclo = c.id
            LEFT JOIN pdca.usuario_ciclo uc ON uc.id_ciclo = c.id
            WHERE c.id_empresa = %s AND c.data_fim_real IS NOT NULL
              AND c.status <> 'CANCELADO'
            GROUP BY c.id
            ORDER BY c.criado_em, c.id;
            """,
            (empresa_id,),
        )

    def cycle_current(self, id_ciclo: int, empresa_id: int) -> dict[str, Any] | None:
        return self.postgres.fetch_one(
            """
            SELECT c.id, c.titulo, c.status, c.data_inicio, c.data_estimada_fim,
                   GREATEST(c.data_estimada_fim - c.data_inicio, 0) AS prazo_planejado_dias,
                   COUNT(DISTINCT pa.id) AS planos,
                   COUNT(DISTINCT t.id) AS tarefas,
                   COUNT(DISTINCT m.id) AS metas,
                   COUNT(DISTINCT p.id) AS problemas,
                   COUNT(DISTINCT uc.id_usuario) AS participantes
            FROM pdca.ciclo c
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = c.id
            LEFT JOIN pdca.tarefa t ON t.id_plano_acao = pa.id
            LEFT JOIN pdca.meta m ON m.id_ciclo = c.id
            LEFT JOIN pdca.problema p ON p.id_ciclo = c.id
            LEFT JOIN pdca.usuario_ciclo uc ON uc.id_ciclo = c.id
            WHERE c.id = %s AND c.id_empresa = %s
            GROUP BY c.id;
            """,
            (id_ciclo, empresa_id),
        )

    def training_completion_training(self, empresa_id: int) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT tr.id, ut.id_usuario,
                   CASE WHEN tr.obrigatorio THEN 1 ELSE 0 END AS obrigatorio_treinamento,
                   CASE WHEN ut.obrigatorio THEN 1 ELSE 0 END AS obrigatorio_usuario,
                   GREATEST(tr.data_treinamento - tr.criado_em::date, 0) AS antecedencia_dias,
                   CASE WHEN ut.status = 'CONCLUIDO' THEN 1 ELSE 0 END AS alvo_conclusao,
                   tr.criado_em
            FROM pdca.usuario_treinamento ut
            JOIN pdca.treinamento tr ON tr.id = ut.id_treinamento
            JOIN pdca.ciclo c ON c.id = tr.id_ciclo
            WHERE c.id_empresa = %s
              AND tr.data_treinamento <= CURRENT_DATE
            ORDER BY tr.criado_em, tr.id, ut.id_usuario;
            """,
            (empresa_id,),
        )

    def training_completion_current(
        self, id_ciclo: int, id_treinamento: int, empresa_id: int
    ) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT tr.id AS id_treinamento, tr.titulo, ut.id_usuario, us.nome AS usuario,
                   CASE WHEN tr.obrigatorio THEN 1 ELSE 0 END AS obrigatorio_treinamento,
                   CASE WHEN ut.obrigatorio THEN 1 ELSE 0 END AS obrigatorio_usuario,
                   GREATEST(tr.data_treinamento - tr.criado_em::date, 0) AS antecedencia_dias
            FROM pdca.usuario_treinamento ut
            JOIN pdca.treinamento tr ON tr.id = ut.id_treinamento
            JOIN pdca.ciclo c ON c.id = tr.id_ciclo
            JOIN usuario_sistema us ON us.id = ut.id_usuario
            WHERE tr.id = %s AND tr.id_ciclo = %s AND c.id_empresa = %s
            ORDER BY us.nome;
            """,
            (id_treinamento, id_ciclo, empresa_id),
        )

    def overload_training(self, empresa_id: int) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT c.id AS id_ciclo, col.id AS id_colaborador,
                   COUNT(t.id) AS total_tarefas,
                   COUNT(t.id) FILTER (WHERE t.prioridade IN ('ALTA','CRITICA')) AS alta_critica,
                   COUNT(t.id) FILTER (WHERE t.status = 'BLOQUEADA') AS bloqueadas,
                   CASE WHEN COUNT(t.id) FILTER (
                       WHERE t.status = 'ATRASADA' OR t.data_fim_real > t.data_fim_prevista
                   ) > 0 THEN 1 ELSE 0 END AS alvo_sobrecarga,
                   c.criado_em
            FROM pdca.ciclo c
            JOIN pdca.usuario_ciclo uc ON uc.id_ciclo = c.id
            JOIN colaborador col ON col.id_usuario = uc.id_usuario
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = c.id
            LEFT JOIN pdca.tarefa t ON t.id_plano_acao = pa.id AND t.id_responsavel = uc.id_usuario
            WHERE c.id_empresa = %s AND c.data_fim_real IS NOT NULL
            GROUP BY c.id, col.id
            ORDER BY c.criado_em, c.id, col.id;
            """,
            (empresa_id,),
        )

    def overload_current(
        self, id_ciclo: int, empresa_id: int, id_colaborador: int | None
    ) -> list[dict[str, Any]]:
        query = """
            SELECT c.id AS id_ciclo, col.id AS id_colaborador, col.nome,
                   COUNT(t.id) FILTER (
                       WHERE t.status NOT IN ('CONCLUIDA','CANCELADA')
                   ) AS total_tarefas,
                   COUNT(t.id) FILTER (
                       WHERE t.status NOT IN ('CONCLUIDA','CANCELADA')
                         AND t.prioridade IN ('ALTA','CRITICA')
                   ) AS alta_critica,
                   COUNT(t.id) FILTER (WHERE t.status = 'BLOQUEADA') AS bloqueadas
            FROM pdca.ciclo c
            JOIN pdca.usuario_ciclo uc ON uc.id_ciclo = c.id
            JOIN colaborador col ON col.id_usuario = uc.id_usuario
            LEFT JOIN pdca.plano_acao pa ON pa.id_ciclo = c.id
            LEFT JOIN pdca.tarefa t ON t.id_plano_acao = pa.id AND t.id_responsavel = uc.id_usuario
            WHERE c.id = %s AND c.id_empresa = %s
        """
        params: list[Any] = [id_ciclo, empresa_id]
        if id_colaborador is not None:
            query += " AND col.id = %s"
            params.append(id_colaborador)
        query += " GROUP BY c.id, col.id, col.nome ORDER BY col.nome;"
        return self.postgres.fetch_all(query, params)

    def goal_training(self, empresa_id: int) -> list[dict[str, Any]]:
        return self.postgres.fetch_all(
            """
            SELECT m.id, COALESCE(m.valor_base, 0) AS valor_base,
                   COALESCE(m.valor_alvo, 0) AS valor_alvo,
                   CASE m.prioridade WHEN 'CRITICA' THEN 4 WHEN 'ALTA' THEN 3
                       WHEN 'MEDIA' THEN 2 ELSE 1 END AS prioridade_ordem,
                   GREATEST(m.prazo - m.criado_em::date, 0) AS prazo_dias,
                   CASE WHEN m.status = 'ATINGIDA' THEN 1 ELSE 0 END AS alvo_atingimento,
                   m.criado_em
            FROM pdca.meta m
            JOIN pdca.ciclo c ON c.id = m.id_ciclo
            WHERE c.id_empresa = %s AND c.data_fim_real IS NOT NULL
              AND m.status <> 'CANCELADA'
            ORDER BY m.criado_em, m.id;
            """,
            (empresa_id,),
        )

    def goal_current(
        self, id_ciclo: int, empresa_id: int, id_meta: int | None
    ) -> list[dict[str, Any]]:
        query = """
            SELECT m.id AS id_meta, m.objetivo, m.status,
                   COALESCE(m.valor_base, 0) AS valor_base,
                   COALESCE(m.valor_alvo, 0) AS valor_alvo,
                   CASE m.prioridade WHEN 'CRITICA' THEN 4 WHEN 'ALTA' THEN 3
                       WHEN 'MEDIA' THEN 2 ELSE 1 END AS prioridade_ordem,
                   GREATEST(m.prazo - m.criado_em::date, 0) AS prazo_dias
            FROM pdca.meta m
            JOIN pdca.ciclo c ON c.id = m.id_ciclo
            WHERE m.id_ciclo = %s AND c.id_empresa = %s
        """
        params: list[Any] = [id_ciclo, empresa_id]
        if id_meta is not None:
            query += " AND m.id = %s"
            params.append(id_meta)
        query += " ORDER BY m.id;"
        return self.postgres.fetch_all(query, params)

    def form_documents(
        self,
        *,
        empresa_id: int,
        id_ciclo: int | None = None,
        id_formulario: str | None = None,
        limit: int = 5000,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        clauses = [_mongo_scope("empresa", empresa_id)]
        if id_ciclo is not None:
            clauses.append(_mongo_scope("ciclo", id_ciclo))
        forms = list(self.database["formularios"].find({"$and": clauses}).limit(limit))

        response_clauses = list(clauses)
        if id_formulario is not None:
            response_clauses.append(_mongo_scope("formulario", id_formulario))
            forms = [
                form
                for form in forms
                if str(
                    form.get("id_formulario")
                    or form.get("formulario_id")
                    or form.get("_id")
                )
                == id_formulario
            ]
        responses = list(
            self.database["respostas_formulario"]
            .find({"$and": response_clauses})
            .limit(limit)
        )
        return serialize(forms), serialize(responses)

    def has_problem_parent(self) -> bool:
        result = self.postgres.fetch_one(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'pdca' AND table_name = 'problema'
                  AND column_name = 'id_problema_pai'
            ) AS existe;
            """
        )
        return bool(result and result["existe"])

    def problem_training(self, empresa_id: int) -> list[dict[str, Any]]:
        if not self.has_problem_parent():
            return []
        return self.postgres.fetch_all(
            """
            SELECT p.id, CONCAT_WS(' ', p.titulo, p.descricao) AS texto,
                   CASE WHEN EXISTS (
                       SELECT 1 FROM pdca.problema filho WHERE filho.id_problema_pai = p.id
                   ) THEN 'RECORRENTE' ELSE 'NAO_RECORRENTE' END AS alvo,
                   p.criado_em
            FROM pdca.problema p
            JOIN pdca.ciclo c ON c.id = p.id_ciclo
            WHERE c.id_empresa = %s
              AND p.status IN ('RESOLVIDO', 'DESCARTADO')
            ORDER BY p.criado_em, p.id;
            """,
            (empresa_id,),
        )

    def problem_current(
        self, id_ciclo: int, empresa_id: int, id_problema: int | None
    ) -> list[dict[str, Any]]:
        query = """
            SELECT p.id AS id_problema, p.titulo, p.descricao,
                   CONCAT_WS(' ', p.titulo, p.descricao) AS texto
            FROM pdca.problema p
            JOIN pdca.ciclo c ON c.id = p.id_ciclo
            WHERE p.id_ciclo = %s AND c.id_empresa = %s
        """
        params: list[Any] = [id_ciclo, empresa_id]
        if id_problema is not None:
            query += " AND p.id = %s"
            params.append(id_problema)
        query += " ORDER BY p.id;"
        return self.postgres.fetch_all(query, params)
