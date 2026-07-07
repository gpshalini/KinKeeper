.PHONY: install playground run test eval

install:
	uv sync

playground:
	export PATH="$$HOME/.local/bin:$$PATH" && uv run agents-cli playground

run:
	uv run python -m app.fast_api_app

test:
	uv run pytest

eval:
	uv run python evals/run_evals.py
