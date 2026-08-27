.PHONY: lint dev tests patch minor

dev:
	uv run main.py

lint:
	uv run ruff check .

tests:
	uv run pytest

patch:
	uv version --bump patch

minor:
	uv version --bump minor
