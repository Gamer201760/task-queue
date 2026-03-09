.PHONY: help run test install lint typecheck pre-commit

help:
	@echo "Доступные команды:"
	@echo "  make run          - Запустить приложение"
	@echo "  make install      - Установить все зависимости"
	@echo "  make test         - Запустить тесты pytest"
	@echo "  make lint         - Запустить линтер ruff"
	@echo "  make typecheck    - Запустить проверку типов mypy"
	@echo "  make pre-commit   - Запустить все проверки (lint, typecheck, test)"

run:
	uv run python -m adapter.cli.main $(ARGS)

install:
	uv sync

test:
	uv run pytest -v

lint:
	uv run ruff check .

typecheck:
	uv run mypy .

pre-commit: lint typecheck test
