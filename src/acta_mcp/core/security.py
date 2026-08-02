import hmac


def constant_time_equals(value: str, expected: str) -> bool:
    return hmac.compare_digest(value.encode("utf-8"), expected.encode("utf-8"))


def parse_positive_int(value: str | None, *, header: str) -> int:
    if value is None:
        raise ValueError(f"Header obrigatório ausente: {header}")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Header inválido: {header}") from exc
    if parsed <= 0:
        raise ValueError(f"Header inválido: {header}")
    return parsed
