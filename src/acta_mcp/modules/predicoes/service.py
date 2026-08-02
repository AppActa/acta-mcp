from datetime import date, timedelta
from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.formularios.repository import document_form_id, response_form_id
from acta_mcp.modules.formularios.service import extract_answers
from acta_mcp.modules.predicoes.modeling import (
    anomaly_detection,
    binary_prediction,
    binary_predictions,
    regression_prediction,
    text_classification,
)
from acta_mcp.modules.predicoes.repository import PredicoesRepository
from acta_mcp.modules.predicoes.schemas import (
    CicloPredicao,
    ColaboradorPredicao,
    FormularioPredicao,
    MetaPredicao,
    ProblemaPredicao,
    TarefaPredicao,
    TreinamentoPredicao,
)

_PRIORITY = {"BAIXA": 1.0, "MEDIA": 2.0, "ALTA": 3.0, "CRITICA": 4.0}
_TASK_FEATURE_NAMES = ["prioridade", "prazo_planejado_dias", "dependencias", "dia_semana"]
_CYCLE_FEATURE_NAMES = [
    "prazo_planejado_dias",
    "planos",
    "tarefas",
    "metas",
    "problemas",
    "participantes",
]
_TRAINING_FEATURE_NAMES = ["obrigatorio_treinamento", "obrigatorio_usuario", "antecedencia_dias"]
_OVERLOAD_FEATURE_NAMES = ["total_tarefas", "tarefas_alta_critica", "tarefas_bloqueadas"]
_GOAL_FEATURE_NAMES = ["valor_base", "valor_alvo", "prioridade", "prazo_dias"]


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_date(value: Any) -> date:
    return date.fromisoformat(str(value).split("T", 1)[0])


def _task_features(row: dict[str, Any]) -> list[float]:
    return [
        _PRIORITY.get(str(row.get("prioridade", "")).upper(), 0.0),
        _number(row.get("prazo_planejado_dias")),
        _number(row.get("dependencias")),
        _number(row.get("dia_semana_criacao")),
    ]


def _cycle_features(row: dict[str, Any]) -> list[float]:
    return [
        _number(row.get("prazo_planejado_dias")),
        _number(row.get("planos")),
        _number(row.get("tarefas")),
        _number(row.get("metas")),
        _number(row.get("problemas")),
        _number(row.get("participantes")),
    ]


def _training_features(row: dict[str, Any]) -> list[float]:
    return [
        _number(row.get("obrigatorio_treinamento")),
        _number(row.get("obrigatorio_usuario")),
        _number(row.get("antecedencia_dias")),
    ]


def _overload_features(row: dict[str, Any]) -> list[float]:
    return [
        _number(row.get("total_tarefas")),
        _number(row.get("alta_critica")),
        _number(row.get("bloqueadas")),
    ]


def _goal_features(row: dict[str, Any]) -> list[float]:
    return [
        _number(row.get("valor_base")),
        _number(row.get("valor_alvo")),
        _number(row.get("prioridade_ordem")),
        _number(row.get("prazo_dias")),
    ]


def _response_text(response: dict[str, Any]) -> str:
    return " | ".join(f"{field}: {value}" for field, value in extract_answers(response))


def _response_id(response: dict[str, Any], index: int) -> str:
    return str(
        response.get("id_resposta")
        or response.get("resposta_id")
        or response.get("_id")
        or f"resposta-{index}"
    )


class PredicoesService:
    def __init__(self, repository: PredicoesRepository, access: AccessService) -> None:
        self.repository = repository
        self.access = access

    def risco_atraso_tarefa(
        self, context: RequestContext, *, id_tarefa: int
    ) -> dict[str, Any]:
        payload = TarefaPredicao(id_tarefa=id_tarefa)
        self.access.ensure_task(context, payload.id_tarefa)
        current = self.repository.task_current(payload.id_tarefa, context.empresa_id)
        if current is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {id_tarefa}.")
        history = self.repository.task_training(context.empresa_id)
        prediction = binary_prediction(
            [_task_features(row) for row in history],
            [int(row["alvo_atraso"]) for row in history],
            _task_features(current),
            feature_names=_TASK_FEATURE_NAMES,
        )
        return {
            "status": "ok",
            "id_tarefa": payload.id_tarefa,
            "titulo": current["titulo"],
            **prediction,
        }

    def estimativa_conclusao_tarefa(
        self, context: RequestContext, *, id_tarefa: int
    ) -> dict[str, Any]:
        payload = TarefaPredicao(id_tarefa=id_tarefa)
        self.access.ensure_task(context, payload.id_tarefa)
        current = self.repository.task_current(payload.id_tarefa, context.empresa_id)
        if current is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {id_tarefa}.")
        history = self.repository.task_training(context.empresa_id)
        prediction = regression_prediction(
            [_task_features(row) for row in history],
            [_number(row["duracao_real_dias"]) for row in history],
            _task_features(current),
            feature_names=_TASK_FEATURE_NAMES,
        )
        response = {
            "status": "ok",
            "id_tarefa": payload.id_tarefa,
            "titulo": current["titulo"],
            **prediction,
        }
        if prediction.get("previsao_disponivel"):
            estimated_days = round(float(prediction["valor_estimado"]))
            estimated_date = _parse_date(current["data_base"]) + timedelta(days=estimated_days)
            due_date = _parse_date(current["data_fim_prevista"])
            response.update(
                {
                    "duracao_estimada_dias": estimated_days,
                    "data_estimada_conclusao": estimated_date.isoformat(),
                    "dias_atraso_estimados": max((estimated_date - due_date).days, 0),
                }
            )
        return response

    def risco_atraso_ciclo(
        self, context: RequestContext, *, id_ciclo: int
    ) -> dict[str, Any]:
        payload = CicloPredicao(id_ciclo=id_ciclo)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.cycle_current(payload.id_ciclo, context.empresa_id)
        if current is None:
            raise NotFoundError(f"Nenhum ciclo encontrado com id {id_ciclo}.")
        history = self.repository.cycle_training(context.empresa_id)
        prediction = binary_prediction(
            [_cycle_features(row) for row in history],
            [int(row["alvo_atraso"]) for row in history],
            _cycle_features(current),
            feature_names=_CYCLE_FEATURE_NAMES,
        )
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "titulo": current["titulo"],
            **prediction,
        }

    def estimativa_conclusao_ciclo(
        self, context: RequestContext, *, id_ciclo: int
    ) -> dict[str, Any]:
        payload = CicloPredicao(id_ciclo=id_ciclo)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.cycle_current(payload.id_ciclo, context.empresa_id)
        if current is None:
            raise NotFoundError(f"Nenhum ciclo encontrado com id {id_ciclo}.")
        history = self.repository.cycle_training(context.empresa_id)
        prediction = regression_prediction(
            [_cycle_features(row) for row in history],
            [_number(row["duracao_real_dias"]) for row in history],
            _cycle_features(current),
            feature_names=_CYCLE_FEATURE_NAMES,
        )
        response = {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "titulo": current["titulo"],
            **prediction,
        }
        if prediction.get("previsao_disponivel"):
            estimated_days = round(float(prediction["valor_estimado"]))
            estimated_date = _parse_date(current["data_inicio"]) + timedelta(days=estimated_days)
            due_date = _parse_date(current["data_estimada_fim"])
            response.update(
                {
                    "duracao_estimada_dias": estimated_days,
                    "data_estimada_conclusao": estimated_date.isoformat(),
                    "dias_atraso_estimados": max((estimated_date - due_date).days, 0),
                }
            )
        return response

    def conclusao_treinamento(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_treinamento: int,
    ) -> dict[str, Any]:
        payload = TreinamentoPredicao(id_ciclo=id_ciclo, id_treinamento=id_treinamento)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.training_completion_current(
            payload.id_ciclo, payload.id_treinamento, context.empresa_id
        )
        if not current:
            raise NotFoundError("Treinamento não encontrado ou sem participantes autorizados.")
        history = self.repository.training_completion_training(context.empresa_id)
        prediction = binary_predictions(
            [_training_features(row) for row in history],
            [int(row["alvo_conclusao"]) for row in history],
            [_training_features(row) for row in current],
            feature_names=_TRAINING_FEATURE_NAMES,
        )
        predictions = prediction.pop("predicoes", [])
        participants = [
            {
                "id_usuario": row["id_usuario"],
                "usuario": row["usuario"],
                **(predictions[index] if predictions else {}),
            }
            for index, row in enumerate(current)
        ]
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "id_treinamento": payload.id_treinamento,
            "participantes": participants,
            **prediction,
        }

    def sobrecarga_colaborador(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_colaborador: int | None = None,
    ) -> dict[str, Any]:
        payload = ColaboradorPredicao(id_ciclo=id_ciclo, id_colaborador=id_colaborador)
        self.access.ensure_cycle(context, payload.id_ciclo)
        if payload.id_colaborador is not None:
            self.access.ensure_collaborator(context, payload.id_colaborador)
        current = self.repository.overload_current(
            payload.id_ciclo, context.empresa_id, payload.id_colaborador
        )
        if not current:
            raise NotFoundError("Nenhum colaborador autorizado encontrado no ciclo.")
        history = self.repository.overload_training(context.empresa_id)
        prediction = binary_predictions(
            [_overload_features(row) for row in history],
            [int(row["alvo_sobrecarga"]) for row in history],
            [_overload_features(row) for row in current],
            feature_names=_OVERLOAD_FEATURE_NAMES,
        )
        predictions = prediction.pop("predicoes", [])
        collaborators = [
            {
                "id_colaborador": row["id_colaborador"],
                "nome": row["nome"],
                "total_tarefas_abertas": int(row["total_tarefas"]),
                **(predictions[index] if predictions else {}),
            }
            for index, row in enumerate(current)
        ]
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "colaboradores": collaborators,
            "definicao_alvo": (
                "Risco histórico de possuir ao menos uma tarefa atrasada; não é uma "
                "avaliação de desempenho individual."
            ),
            **prediction,
        }

    def atingimento_meta(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_meta: int | None = None,
    ) -> dict[str, Any]:
        payload = MetaPredicao(id_ciclo=id_ciclo, id_meta=id_meta)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.goal_current(
            payload.id_ciclo, context.empresa_id, payload.id_meta
        )
        if not current:
            raise NotFoundError("Nenhuma meta autorizada encontrada no ciclo.")
        history = self.repository.goal_training(context.empresa_id)
        prediction = binary_predictions(
            [_goal_features(row) for row in history],
            [int(row["alvo_atingimento"]) for row in history],
            [_goal_features(row) for row in current],
            feature_names=_GOAL_FEATURE_NAMES,
        )
        predictions = prediction.pop("predicoes", [])
        goals = []
        for index, row in enumerate(current):
            item = {
                "id_meta": row["id_meta"],
                "objetivo": row["objetivo"],
                "status_atual": row["status"],
            }
            if predictions:
                item.update(predictions[index])
                item["probabilidade_atingimento"] = item.pop("probabilidade")
                item["risco_nao_atingimento"] = round(
                    1 - item["probabilidade_atingimento"], 6
                )
            goals.append(item)
        return {"status": "ok", "id_ciclo": payload.id_ciclo, "metas": goals, **prediction}

    def respostas_atipicas(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        payload = FormularioPredicao(
            id_ciclo=id_ciclo, id_formulario=id_formulario, limit=limit
        )
        self.access.ensure_cycle(context, payload.id_ciclo)
        _, responses = self.repository.form_documents(
            empresa_id=context.empresa_id,
            id_ciclo=payload.id_ciclo,
            id_formulario=payload.id_formulario,
            limit=payload.limit,
        )
        texts = [_response_text(response) for response in responses]
        prediction = anomaly_detection(texts)
        for result in prediction.get("resultados", []):
            index = result["indice"]
            result["id_resposta"] = _response_id(responses[index], index)
            result.pop("indice")
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "id_formulario": payload.id_formulario,
            **prediction,
        }

    def tema_formulario(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_formulario: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        payload = FormularioPredicao(
            id_ciclo=id_ciclo, id_formulario=id_formulario, limit=limit
        )
        self.access.ensure_cycle(context, payload.id_ciclo)
        training_forms, training_responses = self.repository.form_documents(
            empresa_id=context.empresa_id,
            limit=5000,
        )
        form_labels = {
            identifier: str(
                form.get("tema") or form.get("categoria") or form.get("tipo") or ""
            ).strip()
            for form in training_forms
            if (identifier := document_form_id(form)) is not None
        }
        texts: list[str] = []
        labels: list[str] = []
        for response in training_responses:
            label = str(
                response.get("tema")
                or response.get("categoria")
                or response.get("classificacao")
                or form_labels.get(response_form_id(response) or "", "")
            ).strip()
            text = _response_text(response)
            if label and text:
                texts.append(text)
                labels.append(label.upper())

        _, current = self.repository.form_documents(
            empresa_id=context.empresa_id,
            id_ciclo=payload.id_ciclo,
            id_formulario=payload.id_formulario,
            limit=payload.limit,
        )
        current_texts = [_response_text(response) for response in current]
        if not current_texts:
            return {
                "status": "ok",
                "id_ciclo": payload.id_ciclo,
                "id_formulario": payload.id_formulario,
                "previsao_disponivel": False,
                "motivo": "O formulário não possui respostas analisáveis.",
                "amostras_disponiveis": len(texts),
                "minimo_necessario": 20,
            }
        prediction = text_classification(texts, labels, current_texts)
        for result in prediction.get("resultados", []):
            index = result["indice"]
            result["id_resposta"] = _response_id(current[index], index)
            result.pop("indice")
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "id_formulario": payload.id_formulario,
            **prediction,
        }

    def recorrencia_problema(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_problema: int | None = None,
    ) -> dict[str, Any]:
        payload = ProblemaPredicao(id_ciclo=id_ciclo, id_problema=id_problema)
        self.access.ensure_cycle(context, payload.id_ciclo)
        current = self.repository.problem_current(
            payload.id_ciclo, context.empresa_id, payload.id_problema
        )
        if not current:
            raise NotFoundError("Nenhum problema autorizado encontrado no ciclo.")
        history = self.repository.problem_training(context.empresa_id)
        prediction = text_classification(
            [str(row["texto"]) for row in history],
            [str(row["alvo"]) for row in history],
            [str(row["texto"]) for row in current],
        )
        predictions = prediction.get("resultados", [])
        problems = [
            {
                "id_problema": row["id_problema"],
                "titulo": row["titulo"],
                **(predictions[index] if predictions else {}),
            }
            for index, row in enumerate(current)
        ]
        for item in problems:
            item.pop("indice", None)
        prediction.pop("resultados", None)
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "problemas": problems,
            **prediction,
        }
