from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.predicoes.service import PredicoesService


class FakeAccess:
    def ensure_task(self, *_args) -> None:
        pass

    def ensure_cycle(self, *_args) -> None:
        pass

    def ensure_collaborator(self, *_args) -> None:
        pass


def _history_row(index: int) -> dict[str, Any]:
    return {
        "prioridade": "ALTA" if index % 2 else "MEDIA",
        "prazo_planejado_dias": 10 + index,
        "dependencias": index % 3,
        "dia_semana_criacao": index % 7,
        "alvo_atraso": index % 2,
        "duracao_real_dias": 8 + index,
    }


class FakeRepository:
    def task_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [_history_row(index) for index in range(30)]

    def task_current(self, _id_tarefa: int, _empresa_id: int) -> dict[str, Any]:
        return {
            **_history_row(31),
            "titulo": "Tarefa atual",
            "data_base": "2026-08-01",
            "data_fim_prevista": "2026-09-01",
        }

    def cycle_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [
            {
                "prazo_planejado_dias": 30 + index,
                "planos": 1 + index % 3,
                "tarefas": 4 + index,
                "metas": 1 + index % 2,
                "problemas": index % 4,
                "participantes": 2 + index % 5,
                "alvo_atraso": index % 2,
                "duracao_real_dias": 25 + index,
            }
            for index in range(30)
        ]

    def cycle_current(self, _id_ciclo: int, _empresa_id: int) -> dict[str, Any]:
        return {
            "titulo": "Ciclo atual",
            "status": "EXECUCAO",
            "data_inicio": "2026-08-01",
            "data_estimada_fim": "2026-10-01",
            "prazo_planejado_dias": 61,
            "planos": 3,
            "tarefas": 12,
            "metas": 2,
            "problemas": 2,
            "participantes": 5,
        }

    def training_completion_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [
            {
                "obrigatorio_treinamento": 1,
                "obrigatorio_usuario": index % 2,
                "antecedencia_dias": 5 + index,
                "alvo_conclusao": index % 2,
            }
            for index in range(30)
        ]

    def training_completion_current(self, *_args) -> list[dict[str, Any]]:
        return [
            {
                "id_usuario": 1,
                "usuario": "Ana",
                "obrigatorio_treinamento": 1,
                "obrigatorio_usuario": 1,
                "antecedencia_dias": 10,
            }
        ]

    def overload_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [
            {
                "total_tarefas": 2 + index,
                "alta_critica": index % 4,
                "bloqueadas": index % 2,
                "alvo_sobrecarga": index % 2,
            }
            for index in range(30)
        ]

    def overload_current(self, *_args) -> list[dict[str, Any]]:
        return [
            {
                "id_colaborador": 1,
                "nome": "Ana",
                "total_tarefas": 8,
                "alta_critica": 3,
                "bloqueadas": 1,
            }
        ]

    def goal_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [
            {
                "valor_base": 100 - index,
                "valor_alvo": 80,
                "prioridade_ordem": 1 + index % 4,
                "prazo_dias": 20 + index,
                "alvo_atingimento": index % 2,
            }
            for index in range(30)
        ]

    def goal_current(self, *_args) -> list[dict[str, Any]]:
        return [
            {
                "id_meta": 1,
                "objetivo": "Reduzir retrabalho",
                "status": "EM_ANDAMENTO",
                "valor_base": 100,
                "valor_alvo": 80,
                "unidade": "%",
                "prioridade_ordem": 3,
                "prazo_dias": 30,
            }
        ]

    def form_documents(self, **kwargs):
        if kwargs.get("id_ciclo") is None:
            responses = [
                {
                    "id_resposta": f"historica-{index}",
                    "id_formulario": "historico",
                    "categoria": "MAQUINA" if index % 2 else "METODO",
                    "respostas": {
                        "descricao": (
                            f"vibracao equipamento {index}"
                            if index % 2
                            else f"falha procedimento {index}"
                        )
                    },
                }
                for index in range(24)
            ]
            return [], responses
        responses = [
            {
                "id_resposta": f"atual-{index}",
                "id_formulario": "f-1",
                "respostas": {"descricao": f"vibracao equipamento atual {index}"},
            }
            for index in range(10)
        ]
        responses[-1]["respostas"] = {"descricao": "evento excepcional isolado"}
        return [], responses

    def problem_training(self, _empresa_id: int) -> list[dict[str, Any]]:
        return [
            {
                "texto": (
                    f"problema recorrente vibracao {index}"
                    if index % 2
                    else f"evento unico processo {index}"
                ),
                "alvo": "RECORRENTE" if index % 2 else "NAO_RECORRENTE",
            }
            for index in range(24)
        ]

    def problem_current(self, *_args) -> list[dict[str, Any]]:
        return [
            {
                "id_problema": 1,
                "titulo": "Vibração repetida",
                "texto": "problema recorrente de vibracao",
            }
        ]


def test_all_prediction_services_return_trained_results() -> None:
    context = RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"read"}),
        trace_id="prediction-test",
    )
    service = PredicoesService(FakeRepository(), FakeAccess())

    results = [
        service.risco_atraso_tarefa(context, id_tarefa=1),
        service.estimativa_conclusao_tarefa(context, id_tarefa=1),
        service.risco_atraso_ciclo(context, id_ciclo=1),
        service.estimativa_conclusao_ciclo(context, id_ciclo=1),
        service.conclusao_treinamento(context, id_ciclo=1, id_treinamento=1),
        service.sobrecarga_colaborador(context, id_ciclo=1),
        service.atingimento_meta(context, id_ciclo=1),
        service.respostas_atipicas(context, id_ciclo=1, id_formulario="f-1"),
        service.tema_formulario(context, id_ciclo=1, id_formulario="f-1"),
        service.recorrencia_problema(context, id_ciclo=1),
    ]

    assert all(result["status"] == "ok" for result in results)
    assert all(result["previsao_disponivel"] is True for result in results)
    assert results[6]["metas"][0]["valor_base"] == 100
    assert results[6]["metas"][0]["valor_alvo"] == 80
    assert results[6]["metas"][0]["unidade"] == "%"
