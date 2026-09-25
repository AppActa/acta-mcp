from psycopg_pool import ConnectionPool

from acta_mcp.infrastructure.serializers import serialize


class LicoesRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool

    def company_name(self, *, empresa_id: int) -> str | None:
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT nome FROM empresa WHERE id=%s", (empresa_id,))
            row = cursor.fetchone()
        return row["nome"] if row else None

    def overview(self, *, empresa_id: int, id_ciclo: int) -> dict | None:
        query = """
            WITH cycle_data AS (
                SELECT jsonb_build_object('id', c.id, 'titulo', c.titulo, 'descricao', c.descricao,
                    'status', c.status, 'data_inicio', c.data_inicio, 'data_estimada_fim', c.data_estimada_fim) item
                FROM pdca.ciclo c WHERE c.id = %s AND c.id_empresa = %s
            ), plans AS (
                SELECT coalesce(jsonb_agg(to_jsonb(p)), '[]'::jsonb) item FROM pdca.plano_acao p WHERE p.id_ciclo = %s
            ), goals AS (
                SELECT coalesce(jsonb_agg(to_jsonb(m)), '[]'::jsonb) item FROM pdca.meta m WHERE m.id_ciclo = %s
            ), problems AS (
                SELECT coalesce(jsonb_agg(to_jsonb(p)), '[]'::jsonb) item FROM pdca.problema p WHERE p.id_ciclo = %s
            ), causes AS (
                SELECT coalesce(jsonb_agg(to_jsonb(c)), '[]'::jsonb) item FROM pdca.causa_raiz c WHERE c.id_ciclo = %s
            ), tasks AS (
                SELECT coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) item FROM pdca.tarefa t
                JOIN pdca.plano_acao p ON p.id = t.id_plano_acao WHERE p.id_ciclo = %s
            ), training AS (
                SELECT coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) item FROM pdca.treinamento t WHERE t.id_ciclo = %s
            ), checks AS (
                SELECT coalesce(jsonb_agg(to_jsonb(v)), '[]'::jsonb) item FROM pdca.verificacao_resultado v WHERE v.id_ciclo = %s
            )
            SELECT jsonb_build_object('ciclo', cycle_data.item, 'planos', plans.item, 'metas', goals.item,
                'problemas', problems.item, 'causas_raiz', causes.item, 'tarefas', tasks.item,
                'treinamentos', training.item, 'verificacoes', checks.item) AS overview
            FROM cycle_data, plans, goals, problems, causes, tasks, training, checks
        """
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, (id_ciclo, empresa_id, id_ciclo, id_ciclo, id_ciclo, id_ciclo,
                                   id_ciclo, id_ciclo, id_ciclo))
            row = cursor.fetchone()
        return serialize(row["overview"]) if row else None

    def create_attachment(self, *, usuario_id: int, empresa_id: int, id_ciclo: int,
                          id_licao: int, bucket: str, filename: str, size: int,
                          url: str) -> dict:
        query = """
            INSERT INTO pdca.anexo (id_empresa, id_ciclo, id_origem, nome_arquivo, tipo_arquivo,
                tamanho_arquivo, bucket_arquivo, caminho_arquivo, status, categoria)
            VALUES (%s, %s, %s, %s, 'application/pdf', %s, %s, %s, 'ATIVO', 'LICAO_APRENDIDA')
            RETURNING id, caminho_arquivo
        """
        with (
            self.pool.connection() as connection,
            connection.transaction(),
            connection.cursor() as cursor,
        ):
            cursor.execute("SELECT set_config('app.current_user_id', %s, true)", (str(usuario_id),))
            cursor.execute(query, (empresa_id, id_ciclo, id_licao, filename, size, bucket, url))
            row = cursor.fetchone()
        return {"id_anexo": row["id"], "url": row["caminho_arquivo"]}
