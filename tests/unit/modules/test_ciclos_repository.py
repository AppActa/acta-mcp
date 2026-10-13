from acta_mcp.modules.ciclos.repository import CiclosRepository


class FakePostgres:
    def __init__(self, rows):
        self.rows = rows
        self.query = ""
        self.params = ()

    def fetch_all(self, query, params):
        self.query = query
        self.params = params
        return self.rows


def test_treinamentos_reads_attachments_from_sql_table() -> None:
    rows = [
        {
            "id_treinamento": 12,
            "titulo": "Treinamento",
            "anexos": [
                {
                    "id": 31,
                    "nome_arquivo": "material.pdf",
                    "tipo_arquivo": "application/pdf",
                }
            ],
        }
    ]
    postgres = FakePostgres(rows)

    result = CiclosRepository(postgres).treinamentos(id_ciclo=8, empresa_id=4)

    assert result == rows
    assert postgres.params == (8, 4)
    assert "pdca.anexo" in postgres.query
    assert "id_anexo_mongo" not in postgres.query
    assert "'TREINAMENTO'" in postgres.query
    assert "id_origem" in postgres.query
    assert "jsonb_agg" in postgres.query
    assert "a.id_empresa = c.id_empresa" in postgres.query
    assert "a.id_ciclo = tr.id_ciclo" in postgres.query
    assert "a.status = 'ATIVO'" in postgres.query
    assert "a.excluido_em IS NULL" in postgres.query
