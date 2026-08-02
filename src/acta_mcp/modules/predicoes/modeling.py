from hashlib import sha256
from typing import Any

import numpy as np
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    IsolationForest,
    RandomForestRegressor,
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

MIN_CLASSIFICATION_SAMPLES = 20
MIN_REGRESSION_SAMPLES = 15
MIN_TEXT_SAMPLES = 20
MIN_ANOMALY_SAMPLES = 8


def unavailable(reason: str, available: int, minimum: int) -> dict[str, Any]:
    return {
        "previsao_disponivel": False,
        "motivo": reason,
        "amostras_disponiveis": available,
        "minimo_necessario": minimum,
    }


def _version(kind: str, features: list[list[float]], targets: list[Any]) -> str:
    digest = sha256(repr((features, targets)).encode()).hexdigest()[:12]
    return f"{kind}-{digest}"


def binary_prediction(
    features: list[list[float]],
    targets: list[int],
    current: list[float],
    *,
    feature_names: list[str],
    minimum: int = MIN_CLASSIFICATION_SAMPLES,
) -> dict[str, Any]:
    result = binary_predictions(
        features,
        targets,
        [current],
        feature_names=feature_names,
        minimum=minimum,
    )
    if result.get("previsao_disponivel"):
        prediction = result.pop("predicoes")[0]
        result.update(prediction)
    return result


def binary_predictions(
    features: list[list[float]],
    targets: list[int],
    currents: list[list[float]],
    *,
    feature_names: list[str],
    minimum: int = MIN_CLASSIFICATION_SAMPLES,
) -> dict[str, Any]:
    if len(features) < minimum:
        return unavailable("Histórico insuficiente para classificação.", len(features), minimum)
    if len(set(targets)) < 2:
        return unavailable("O histórico possui apenas uma classe de resultado.", len(features), minimum)
    if min(targets.count(0), targets.count(1)) < 3:
        return unavailable("Uma das classes possui menos de três resultados.", len(features), minimum)

    use_boosting = len(features) >= 50 and min(targets.count(0), targets.count(1)) >= 10
    estimator = (
        HistGradientBoostingClassifier(max_iter=120, random_state=42)
        if use_boosting
        else LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    )
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), estimator)

    metrics: dict[str, float] = {}
    split = max(minimum // 2, int(len(features) * 0.8))
    if split < len(features) and len(set(targets[:split])) == 2:
        model.fit(features[:split], targets[:split])
        test_probability = model.predict_proba(features[split:])[:, 1]
        test_prediction = (test_probability >= 0.5).astype(int)
        metrics["acuracia_temporal"] = round(
            float(accuracy_score(targets[split:], test_prediction)), 4
        )
        metrics["brier_score"] = round(
            float(brier_score_loss(targets[split:], test_probability)), 4
        )

    model.fit(features, targets)
    probabilities = model.predict_proba(currents)[:, 1]
    return {
        "previsao_disponivel": True,
        "predicoes": [
            {
                "probabilidade": round(float(probability), 6),
                "classificacao": (
                    "ALTO" if probability >= 0.7 else "MEDIO" if probability >= 0.4 else "BAIXO"
                ),
            }
            for probability in probabilities
        ],
        "modelo": {
            "algoritmo": type(estimator).__name__,
            "versao": _version("classificacao", features, targets),
            "amostras_treinamento": len(features),
            "features": feature_names,
            "metricas": metrics,
        },
    }


def regression_prediction(
    features: list[list[float]],
    targets: list[float],
    current: list[float],
    *,
    feature_names: list[str],
    minimum: int = MIN_REGRESSION_SAMPLES,
) -> dict[str, Any]:
    if len(features) < minimum:
        return unavailable("Histórico insuficiente para regressão.", len(features), minimum)
    if len(set(round(value, 6) for value in targets)) < 2:
        return unavailable("O histórico não possui variação no resultado.", len(features), minimum)

    estimator = (
        HistGradientBoostingRegressor(loss="absolute_error", max_iter=120, random_state=42)
        if len(features) >= 50
        else RandomForestRegressor(
            n_estimators=120,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=1,
        )
    )
    # O transformador impede previsões negativas para durações sem alterar o alvo salvo.
    model = TransformedTargetRegressor(
        regressor=make_pipeline(SimpleImputer(strategy="median"), estimator),
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )
    metrics: dict[str, float] = {}
    split = max(minimum // 2, int(len(features) * 0.8))
    if split < len(features):
        model.fit(features[:split], targets[:split])
        test_prediction = np.maximum(model.predict(features[split:]), 0)
        metrics["mae_temporal"] = round(
            float(mean_absolute_error(targets[split:], test_prediction)), 4
        )

    model.fit(features, targets)
    prediction = max(float(model.predict([current])[0]), 0.0)
    return {
        "previsao_disponivel": True,
        "valor_estimado": round(prediction, 4),
        "modelo": {
            "algoritmo": type(estimator).__name__,
            "versao": _version("regressao", features, targets),
            "amostras_treinamento": len(features),
            "features": feature_names,
            "metricas": metrics,
        },
    }


def anomaly_detection(texts: list[str]) -> dict[str, Any]:
    usable = [text.strip() for text in texts if text.strip()]
    if len(usable) < MIN_ANOMALY_SAMPLES:
        return unavailable(
            "São necessárias mais respostas para detectar anomalias.",
            len(usable),
            MIN_ANOMALY_SAMPLES,
        )
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(usable)
    except ValueError:
        return unavailable("As respostas não contêm texto analisável.", len(usable), MIN_ANOMALY_SAMPLES)
    model = IsolationForest(random_state=42, contamination="auto")
    labels = model.fit_predict(matrix)
    scores = -model.decision_function(matrix)
    results = [
        {
            "indice": index,
            "atipica": bool(label == -1),
            "indice_anomalia": round(float(score), 6),
        }
        for index, (label, score) in enumerate(zip(labels, scores, strict=True))
    ]
    return {
        "previsao_disponivel": True,
        "total_analisado": len(results),
        "total_atipicas": sum(item["atipica"] for item in results),
        "resultados": results,
        "modelo": {
            "algoritmo": "TfidfVectorizer+IsolationForest",
            "versao": _version("anomalia", [[float(len(text))] for text in usable], []),
            "amostras_treinamento": len(usable),
        },
    }


def text_classification(
    texts: list[str],
    labels: list[str],
    current_texts: list[str],
    *,
    minimum: int = MIN_TEXT_SAMPLES,
) -> dict[str, Any]:
    if len(texts) < minimum:
        return unavailable("Histórico textual rotulado insuficiente.", len(texts), minimum)
    if len(set(labels)) < 2:
        return unavailable("O histórico textual possui apenas uma categoria.", len(texts), minimum)
    if min(labels.count(label) for label in set(labels)) < 2:
        return unavailable("Há categorias com apenas uma amostra.", len(texts), minimum)
    model = make_pipeline(
        TfidfVectorizer(max_features=1000, ngram_range=(1, 2)),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )
    model.fit(texts, labels)
    probabilities = model.predict_proba(current_texts)
    classes = list(model.classes_)
    results = []
    for index, row in enumerate(probabilities):
        best = int(np.argmax(row))
        results.append(
            {
                "indice": index,
                "classe": classes[best],
                "probabilidade": round(float(row[best]), 6),
            }
        )
    return {
        "previsao_disponivel": True,
        "resultados": results,
        "modelo": {
            "algoritmo": "TfidfVectorizer+LogisticRegression",
            "versao": _version("texto", [[float(len(text))] for text in texts], labels),
            "amostras_treinamento": len(texts),
            "classes": classes,
        },
    }
