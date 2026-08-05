from acta_mcp.core.context import RequestContext
from acta_mcp.modules.relatorios.service import RelatoriosService


class FakeAccess:
    def ensure_cycle(self, context, id_ciclo) -> None:
        assert context.empresa_id == 1
        assert id_ciclo == 1


class FakeCiclos:
    def visao_geral(self, *_):
        return {"status": "ok", "ciclo": {"titulo": "Ciclo", "email": "oculto"}}

    def problema_principal(self, *_):
        return {"status": "ok", "problema": "Retrabalho"}

    def causas_raiz(self, *_):
        return {"status": "ok", "causas": []}

    def ishikawa(self, *_):
        return {"status": "ok", "diagramas": []}

    def riscos_pendencias(self, *_):
        return {"status": "ok", "riscos": []}

    def treinamentos(self, *_):
        return {"status": "ok", "treinamentos": []}


class FakeTarefas:
    def relatorio(self, *_):
        return {"status": "ok", "tarefas_gerais": []}


class FakeColaboradores:
    def participantes(self, *_):
        return {"status": "ok", "participantes": []}

    def carga_trabalho(self, *_):
        return {"status": "ok", "carga_trabalho": []}


class FakeFormularios:
    def resumo_respostas(self, *_, **__):
        return {
            "status": "ok",
            "total_formularios": 1,
            "total_respostas": 2,
            "formularios": [{"id": "omitido"}],
            "respostas": [{"cpf": "omitido"}],
        }


def test_contexto_ciclo_consolidates_current_data_without_persisted_reports() -> None:
    context = RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"read"}),
        trace_id="test",
    )
    service = RelatoriosService(
        FakeAccess(),
        FakeCiclos(),
        FakeTarefas(),
        FakeColaboradores(),
        FakeFormularios(),
    )

    result = service.contexto_ciclo(context, id_ciclo=1)

    assert result["status"] == "ok"
    assert result["somente_leitura"] is True
    assert result["formularios"] == {
        "status": "ok",
        "total_formularios": 1,
        "total_respostas": 2,
    }
    assert "relatorios_existentes" not in result
    assert "email" not in str(result).lower()
