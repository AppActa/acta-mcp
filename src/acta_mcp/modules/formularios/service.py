from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.modules.common import AccessService, normalize_optional_text
from acta_mcp.modules.formularios.repository import (
    FormulariosRepository,
    response_form_id,
)
from acta_mcp.modules.formularios.schemas import (
    FormularioCreate,
    FormularioPublish,
    FormulariosQuery,
    PerguntaCreate,
    RespostasFormularioQuery,
)

_ANSWER_CONTAINERS = ("respostas", "answers", "campos", "fields")
_QUESTION_FIELDS = ("pergunta", "questao", "question", "campo", "label", "nome")
_ANSWER_FIELDS = ("resposta", "answer", "valor", "value")
_METADATA_FIELDS = {
    "_id",
    "id",
    "id_ciclo",
    "ciclo_id",
    "idCiclo",
    "cicloId",
    "id_empresa",
    "empresa_id",
    "idEmpresa",
    "empresaId",
    "id_formulario",
    "formulario_id",
    "idFormulario",
    "formularioId",
    "id_resposta",
    "resposta_id",
    "id_usuario",
    "usuario_id",
    "id_colaborador",
    "colaborador_id",
    "criado_em",
    "atualizado_em",
    "respondido_em",
    "created_at",
    "updated_at",
}


def _first(document: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if document.get(name) is not None:
            return document[name]
    return None


def _flatten(prefix: str, value: Any) -> list[tuple[str, Any]]:
    if isinstance(value, dict):
        question = _first(value, _QUESTION_FIELDS)
        answer = _first(value, _ANSWER_FIELDS)
        if question is not None and answer is not None:
            return _flatten(str(question), answer)
        flattened: list[tuple[str, Any]] = []
        for key, nested in value.items():
            field = f"{prefix}.{key}" if prefix else str(key)
            flattened.extend(_flatten(field, nested))
        return flattened
    if isinstance(value, list):
        flattened = []
        for item in value:
            flattened.extend(_flatten(prefix, item))
        return flattened
    if value is None or value == "":
        return []
    return [(prefix or "resposta", value)]


def extract_answers(document: dict[str, Any]) -> list[tuple[str, Any]]:
    for container in _ANSWER_CONTAINERS:
        if container in document:
            return _flatten("", document[container])
    return [
        pair
        for key, value in document.items()
        if key not in _METADATA_FIELDS
        for pair in _flatten(key, value)
    ]


def _matches(document: dict[str, Any], names: tuple[str, ...], expected: str | None) -> bool:
    if expected is None:
        return True
    value = _first(document, names)
    return value is not None and str(value).strip().casefold() == expected.casefold()


class FormulariosService:
    def __init__(
        self,
        repository: FormulariosRepository,
        access: AccessService,
    ) -> None:
        self.repository = repository
        self.access = access

    def listar(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str | None = None,
        tipo: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        self.access.ensure_cycle(context, id_ciclo)
        query = FormulariosQuery(
            id_ciclo=id_ciclo,
            id_formulario=id_formulario,
            tipo=normalize_optional_text(tipo),
            status=normalize_optional_text(status),
            limit=limit,
        )
        if query.id_formulario is not None:
            form = self.repository.obter_formulario(
                id_ciclo=id_ciclo,
                empresa_id=context.empresa_id,
                id_formulario=query.id_formulario,
            )
            forms = [form] if form is not None else []
        else:
            forms = self.repository.listar_formularios(
                id_ciclo=id_ciclo,
                empresa_id=context.empresa_id,
                limit=query.limit,
            )
        forms = [
            form
            for form in forms
            if _matches(form, ("tipo", "type", "categoria"), query.tipo)
            and _matches(form, ("status", "situacao"), query.status)
        ]
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "count": len(forms),
            "formularios": forms,
        }

    def respostas(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        self.access.ensure_cycle(context, id_ciclo)
        query = RespostasFormularioQuery(
            id_ciclo=id_ciclo,
            id_formulario=id_formulario,
            limit=limit,
        )
        forms_result = self.listar(
            context,
            id_ciclo=id_ciclo,
            id_formulario=query.id_formulario,
            limit=200,
        )
        forms = forms_result["formularios"]
        if query.id_formulario is not None and not forms:
            raise NotFoundError(
                f"Nenhum formulário autorizado encontrado com id {query.id_formulario}."
            )
        responses = self.repository.listar_respostas(
            id_ciclo=id_ciclo,
            empresa_id=context.empresa_id,
            formularios=forms,
            id_formulario=query.id_formulario,
            limit=query.limit,
        )
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "id_formulario": query.id_formulario,
            "count": len(responses),
            "respostas": responses,
        }

    def detalhes(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str,
        limit_respostas: int = 100,
    ) -> dict[str, Any]:
        forms = self.listar(
            context,
            id_ciclo=id_ciclo,
            id_formulario=id_formulario,
            limit=1,
        )["formularios"]
        if not forms:
            raise NotFoundError(f"Nenhum formulário autorizado encontrado com id {id_formulario}.")
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "formulario": forms[0],
            "respostas": self.respostas(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                limit=limit_respostas,
            ),
        }

    def resumo_respostas(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        forms = self.listar(
            context,
            id_ciclo=id_ciclo,
            id_formulario=id_formulario,
            limit=200,
        )["formularios"]
        responses = self.respostas(
            context,
            id_ciclo=id_ciclo,
            id_formulario=id_formulario,
            limit=limit,
        )["respostas"]

        field_counts: Counter[str] = Counter()
        value_counts: dict[str, Counter[str]] = defaultdict(Counter)
        response_counts: Counter[str] = Counter()
        display_values: dict[tuple[str, str], Any] = {}
        for response in responses:
            form_id = response_form_id(response) or "sem_formulario"
            response_counts[form_id] += 1
            for field, value in extract_answers(response):
                field_counts[field] += 1
                if isinstance(value, (str, int, float, bool)):
                    text = str(value).strip()
                    if text and len(text) <= 160:
                        normalized = text.casefold()
                        value_counts[field][normalized] += 1
                        display_values.setdefault((field, normalized), value)

        patterns = []
        for field, counter in value_counts.items():
            for normalized, count in counter.most_common(5):
                if count >= 2:
                    patterns.append(
                        {
                            "campo": field,
                            "valor": display_values[(field, normalized)],
                            "ocorrencias": count,
                            "percentual_respostas": round(count * 100 / max(len(responses), 1), 2),
                        }
                    )
        patterns.sort(key=lambda item: (-item["ocorrencias"], item["campo"]))

        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "id_formulario": id_formulario,
            "total_formularios": len(forms),
            "total_respostas": len(responses),
            "respostas_por_formulario": dict(response_counts),
            "campos_mais_respondidos": [
                {"campo": field, "respostas": count}
                for field, count in field_counts.most_common(20)
            ],
            "padroes_repetidos": patterns[:20],
            "formularios": forms,
            "respostas": responses,
        }

    def criar_rascunho(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        titulo: str,
        tipo: str,
        descricao: str | None = None,
    ) -> dict[str, Any]:
        payload = FormularioCreate(
            id_ciclo=id_ciclo,
            titulo=titulo,
            tipo=tipo,
            descricao=descricao,
        )
        self.access.ensure_cycle(context, payload.id_ciclo)
        now = datetime.now(UTC)
        document = {
            "_id": str(uuid4()),
            "id_formulario": str(uuid4()),
            "id_ciclo": payload.id_ciclo,
            "id_empresa": context.empresa_id,
            "titulo": payload.titulo.strip(),
            "tipo": payload.tipo.strip().upper(),
            "descricao": payload.descricao.strip() if payload.descricao else None,
            "status": "RASCUNHO",
            "perguntas": [],
            "criado_por": context.usuario_id,
            "criado_em": now,
            "atualizado_em": now,
        }
        return {"status": "ok", "formulario": self.repository.criar(document)}

    def adicionar_pergunta(self, context: RequestContext, **data) -> dict[str, Any]:
        payload = PerguntaCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        is_selection = payload.tipo_resposta in {"SELECAO_UNICA", "MULTIPLA"}
        if is_selection and not payload.opcoes:
            raise ValueError("Perguntas de seleção devem possuir ao menos uma opção.")
        if not is_selection and payload.opcoes:
            raise ValueError("Opções são permitidas apenas em perguntas de seleção.")
        options = [option.strip() for option in payload.opcoes if option.strip()]
        if len(options) != len(set(option.casefold() for option in options)):
            raise ValueError("As opções da pergunta não podem se repetir.")
        question = {
            "id_pergunta": str(uuid4()),
            "texto": payload.texto.strip(),
            "tipo_resposta": payload.tipo_resposta,
            "obrigatoria": payload.obrigatoria,
            "opcoes": options,
        }
        form = self.repository.adicionar_pergunta(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            id_formulario=payload.id_formulario,
            pergunta=question,
            atualizado_em=datetime.now(UTC),
        )
        if form is None:
            raise NotFoundError("Formulário rascunho não encontrado ou já publicado.")
        return {"status": "ok", "formulario": form, "pergunta": question}

    def publicar(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str,
    ) -> dict[str, Any]:
        payload = FormularioPublish(id_ciclo=id_ciclo, id_formulario=id_formulario)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.obter_formulario(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            id_formulario=payload.id_formulario,
        )
        if current is None:
            raise NotFoundError("Formulário não encontrado.")
        if not current.get("perguntas") and not current.get("campos"):
            raise ValueError("Adicione ao menos uma pergunta antes de publicar o formulário.")
        form = self.repository.publicar(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            id_formulario=payload.id_formulario,
            atualizado_em=datetime.now(UTC),
        )
        return {"status": "ok", "formulario": form}
