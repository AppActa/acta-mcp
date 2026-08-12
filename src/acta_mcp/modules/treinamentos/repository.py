from typing import Any

from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.infrastructure.serializers import serialize
from acta_mcp.modules.treinamentos.schemas import TreinamentoCreate


class TreinamentosRepository:
    def __init__(self, postgres: PostgresRepository) -> None:
        self.postgres = postgres

    def criar(self, payload: TreinamentoCreate) -> dict[str, Any]:
        with (
            self.postgres.pool.connection() as connection,
            connection.transaction(),
            connection.cursor() as cursor,
        ):
            cursor.execute(
                """
                    INSERT INTO pdca.treinamento (
                        id_ciclo, id_responsavel, titulo, descricao,
                        data_treinamento, obrigatorio
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *;
                    """,
                (
                    payload.id_ciclo,
                    payload.id_responsavel,
                    payload.titulo,
                    payload.descricao,
                    payload.data_treinamento,
                    payload.obrigatorio,
                ),
            )
            training = dict(cursor.fetchone())
            if payload.participantes:
                cursor.executemany(
                    """
                        INSERT INTO pdca.usuario_treinamento (
                            id_treinamento, id_usuario, obrigatorio, status
                        ) VALUES (%s, %s, %s, 'PENDENTE');
                        """,
                    [
                        (training["id"], user_id, payload.obrigatorio)
                        for user_id in payload.participantes
                    ],
                )
        return serialize(training)
