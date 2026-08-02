from acta_mcp.modules.predicoes.modeling import (
    anomaly_detection,
    binary_prediction,
    regression_prediction,
    text_classification,
)


def test_binary_prediction_trains_and_returns_probability() -> None:
    features = [[float(index), float(index % 3)] for index in range(40)]
    targets = [int(index >= 20) for index in range(40)]

    result = binary_prediction(
        features,
        targets,
        [35.0, 2.0],
        feature_names=["progresso", "prioridade"],
    )

    assert result["previsao_disponivel"] is True
    assert 0 <= result["probabilidade"] <= 1
    assert result["modelo"]["amostras_treinamento"] == 40


def test_regression_prediction_trains_and_returns_non_negative_value() -> None:
    features = [[float(index), float(index % 4)] for index in range(30)]
    targets = [float(index + 3) for index in range(30)]

    result = regression_prediction(
        features,
        targets,
        [25.0, 1.0],
        feature_names=["prazo", "dependencias"],
    )

    assert result["previsao_disponivel"] is True
    assert result["valor_estimado"] >= 0


def test_models_report_insufficient_data_without_fabricating_result() -> None:
    result = binary_prediction(
        [[1.0], [2.0]],
        [0, 1],
        [3.0],
        feature_names=["valor"],
    )

    assert result["previsao_disponivel"] is False
    assert "probabilidade" not in result


def test_text_models_execute_with_sufficient_samples() -> None:
    texts = [f"falha maquina vibracao {index}" for index in range(12)] + [
        f"erro processo metodo {index}" for index in range(12)
    ]
    labels = ["MAQUINA"] * 12 + ["METODO"] * 12

    classification = text_classification(texts, labels, ["maquina com vibracao"])
    anomalies = anomaly_detection([*texts[:9], "evento completamente incomum isolado"])

    assert classification["previsao_disponivel"] is True
    assert classification["resultados"][0]["classe"] == "MAQUINA"
    assert anomalies["previsao_disponivel"] is True
    assert anomalies["total_analisado"] == 10
