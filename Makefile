.PHONY: lint dev tests

dev:
	uv run main.py

lint:
	uv run ruff check .

tests:
	uv run pytest