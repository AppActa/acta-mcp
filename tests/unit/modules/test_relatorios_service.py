from acta_mcp.core.context import RequestContext
from acta_mcp.modules.relatorios.service import RelatoriosService


class FakeAccess:
    def ensure_cycle(self, context, id_ciclo) -> None:
        assert context.empresa_id == 1
        assert id_ciclo == 1


class FakeRepository:
    def listar(self, **_) -> list[dict]:
        return [{"id_relatorio": "r-1", "email": "oculto@acta.local"}]

    def obter(self, **_) -> dict:
        return {"id_relatorio": "r-1", "conteudo": {"cpf": "123", "texto": "ok"}}

    def mais_recente(self, **_) -> dict:
        return {"id_relatorio": "r-1", "senha_hash": "oculta"}


class UnusedService:
    pass


def _service() -> RelatoriosService:
    unused = UnusedService()
    return RelatoriosService(
        FakeRepository(),
        FakeAccess(),
        unused,
        unused,
        unused,
        unused,
    )


def test_report_reads_remove_sensitive_fields() -> None:
    context = RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"read"}),
        trace_id="test",
    )
    service = _service()

    listed = service.listar(context, id_ciclo=1)
    detailed = service.detalhes(context, id_ciclo=1, id_relatorio="r-1")
    latest = service.mais_recente(context, id_ciclo=1)

    assert "email" not in listed["relatorios"][0]
    assert detailed["relatorio"]["conteudo"] == {"texto": "ok"}
    assert "senha_hash" not in latest["relatorio"]
