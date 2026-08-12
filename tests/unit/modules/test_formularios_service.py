from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.formularios.service import FormulariosService


class FakeAccess:
    def __init__(self) -> None:
        self.cycles: list[int] = []

    def ensure_cycle(self, _context: RequestContext, id_ciclo: int) -> None:
        self.cycles.append(id_ciclo)


class FakeRepository:
    forms = [
        {
            "id_formulario": "f-1",
            "id_ciclo": 1,
            "id_empresa": 1,
            "titulo": "Fenômeno",
            "tipo": "ANALISE_FENOMENO",
            "status": "ATIVO",
        }
    ]
    responses = [
        {
            "id_formulario": "f-1",
            "respostas": {"Turno": "Noite", "Sintoma": "Retrabalho"},
        },
        {
            "id_formulario": "f-1",
            "respostas": [
                {"pergunta": "Turno", "resposta": "Noite"},
                {"pergunta": "Sintoma", "resposta": "Retrabalho"},
            ],
        },
    ]

    def listar_formularios(self, **_: Any) -> list[dict[str, Any]]:
        return self.forms

    def obter_formulario(self, **kwargs: Any) -> dict[str, Any] | None:
        return self.forms[0] if kwargs["id_formulario"] == "f-1" else None

    def listar_respostas(self, **_: Any) -> list[dict[str, Any]]:
        return self.responses


def _context() -> RequestContext:
    return RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"read"}),
        trace_id="forms-test",
    )


def test_summary_finds_repeated_patterns() -> None:
    access = FakeAccess()
    service = FormulariosService(FakeRepository(), access)  # type: ignore[arg-type]

    result = service.resumo_respostas(_context(), id_ciclo=1)

    assert result["status"] == "ok"
    assert result["total_formularios"] == 1
    assert result["total_respostas"] == 2
    assert {
        (pattern["campo"], pattern["valor"], pattern["ocorrencias"])
        for pattern in result["padroes_repetidos"]
    } == {("Sintoma", "Retrabalho", 2), ("Turno", "Noite", 2)}
    assert access.cycles


def test_list_filters_type_and_status() -> None:
    service = FormulariosService(FakeRepository(), FakeAccess())  # type: ignore[arg-type]

    found = service.listar(
        _context(),
        id_ciclo=1,
        tipo="analise_fenomeno",
        status="ativo",
    )
    missing = service.listar(_context(), id_ciclo=1, status="inativo")

    assert found["count"] == 1
    assert missing["count"] == 0
