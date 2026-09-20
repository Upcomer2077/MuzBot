.PHONY: lint dev test patch minor

dev:
	uv run main.py

lint:
	uv run ruff check .

test:
	uv run pytest

patch:
	uv version --bump patch

minor:
	uv version --bump minor
