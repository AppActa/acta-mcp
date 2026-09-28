import sys
from types import SimpleNamespace

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.licoes.repository import LicoesRepository
from acta_mcp.modules.licoes.service import LicoesService


class LessonsCollection:
    def __init__(self, records):
        self.records = records
        self.query = None

    def find(self, query, _projection):
        self.query = query
        return self

    def sort(self, *_args):
        return self.records


class Access:
    def __init__(self):
        self.checked = []

    def ensure_cycle(self, context, cycle_id):
        self.checked.append((context.empresa_id, cycle_id))


def make_service(records):
    collection = LessonsCollection(records)
    mongo = SimpleNamespace(database={"licoes_aprendidas": collection})
    access = Access()
    service = LicoesService(mongo, object(), access, object())
    service._model = lambda: SimpleNamespace(
        invoke=lambda _prompt: SimpleNamespace(content="As causas foram verificadas antes da ação.")
    )
    context = RequestContext(usuario_id=3, empresa_id=4, permissoes=frozenset({"read"}), trace_id="t")
    return service, collection, access, context


def test_question_uses_company_cycle_filter_and_returns_lesson_references():
    service, collection, access, context = make_service([{"id_licao": 21, "licao": "Evidência"}])

    result = service.perguntar(context, id_ciclo=9, pergunta="O que aprendemos?")

    assert collection.query == {"id_empresa": 4, "id_ciclo": 9}
    assert access.checked == [(4, 9)]
    assert result == {
        "status": "ok",
        "resposta": "As causas foram verificadas antes da ação.",
        "referencias": [21],
    }


def test_question_without_lesson_evidence_returns_empty_status():
    service, collection, _access, context = make_service([])

    assert service.perguntar(context, id_ciclo=9, pergunta="O que aprendemos?") == {
        "status": "sem_evidencia"
    }
    assert collection.query == {"id_empresa": 4, "id_ciclo": 9}


def test_repository_reads_dict_row_factory_results():
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def execute(self, _query, _params=()):
            pass

        def fetchone(self):
            return {
                "overview": {"ciclo": {"id": 9}},
                "id": 18,
                "caminho_arquivo": "https://example.test/licao.pdf",
            }

        def close(self):
            pass

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def cursor(self):
            return Cursor()

        def transaction(self):
            return self

    class Pool:
        def connection(self):
            return Connection()

    repository = LicoesRepository(Pool())

    assert repository.overview(empresa_id=4, id_ciclo=9) == {"ciclo": {"id": 9}}
    assert repository.create_attachment(
        usuario_id=3,
        empresa_id=4,
        id_ciclo=9,
        id_licao=27,
        filename="licao-27.pdf",
        size=100,
        bucket="empresa-4",
        url="https://example.test/licao.pdf",
    ) == {"id_anexo": 18, "url": "https://example.test/licao.pdf"}


def test_create_generates_pdf_and_persists_lesson_and_attachment(monkeypatch):
    class Collection:
        def __init__(self):
            self.inserted = None
            self.deleted = []

        def find(self, *_args):
            return self

        def sort(self, *_args):
            return [{"relatorio": "evidência de teste"}] * 5

        def insert_one(self, value):
            self.inserted = value

        def delete_one(self, query):
            self.deleted.append(query)

    class Counters:
        def find_one_and_update(self, *_args, **_kwargs):
            return {"seq": 22}

    reports, lessons = Collection(), Collection()
    database = {"relatorios": reports, "licoes_aprendidas": lessons, "counters": Counters()}
    service, _collection, access, context = make_service([])
    service.mongo = SimpleNamespace(database=database)
    service.repository = SimpleNamespace(
        company_name=lambda **_kwargs: "Empresa Teste",
        create_attachment=lambda **kwargs: {"id_anexo": 31, "url": kwargs["url"]},
    )
    service.settings = SimpleNamespace(
        gemini_api_key="test", cloudinary_cloud_name="cloud", cloudinary_api_key="key",
        cloudinary_api_secret="secret",
    )
    service._model = lambda: SimpleNamespace(
        invoke=lambda _prompt: SimpleNamespace(
            content='{"titulo":"Lição","licao":"Revisar evidências","categoria":"processo","tags":[]}'
        )
    )
    uploaded_files = []
    cloudinary = SimpleNamespace(
        config=lambda **_kwargs: None,
        uploader=SimpleNamespace(
            upload=lambda body, **_kwargs: uploaded_files.append(body) or {
                "public_id": "empresa-teste/licao-22", "secure_url": "https://example.test/22.pdf"
            },
            destroy=lambda *_args, **_kwargs: None,
        ),
    )
    monkeypatch.setitem(sys.modules, "cloudinary", cloudinary)

    result = service.criar(context, id_ciclo=9, contexto="falha", expectativa="evitar recorrência")

    assert result["status"] == "ok"
    assert result["licao"]["id_licao"] == 22
    assert result["anexo"]["id_anexo"] == 31
    assert reports.find({}, {"_id": 0}).sort("criado_em", -1) == [
        {"relatorio": "evidência de teste"}
    ] * 5
    assert len(uploaded_files) == 1 and uploaded_files[0].startswith(b"%PDF")
    assert lessons.inserted["id_empresa"] == context.empresa_id
    assert access.checked == [(context.empresa_id, 9)]
