UV ?= uv
COMPOSE ?= docker compose
COVERAGE_MIN ?= 80

TEST_DATABASE_URL ?= postgresql://acta:acta@localhost:5433/acta
TEST_MONGODB_URI ?= mongodb://localhost:27018
export TEST_DATABASE_URL TEST_MONGODB_URI

.PHONY: validate

validate:
	$(UV) sync --frozen --extra dev
	$(UV) lock --check
	$(COMPOSE) config -q
	$(COMPOSE) up -d --wait postgres mongodb
	$(UV) run ruff check src tests
	$(UV) run pytest -q --cov=acta_mcp --cov-report=term-missing --cov-fail-under=$(COVERAGE_MIN)
	@echo VALIDATE APROVADO: Ruff 100% sem findings; testes aprovados; cobertura >= $(COVERAGE_MIN)%.

