.PHONY: check format lint test docker-build docker-run docker-scan
PROJECT_NAME=polygraph
UV_CMD := $(shell command -v uv >/dev/null 2>&1 && echo "uv run " || echo "")
TAG := latest

check: format lint test

deps:
	if command -v uv >/dev/null 2>&1; then \
		echo "uv is already installed"; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | bash; \
	fi
	$(UV_CMD) sync

format:
	$(UV_CMD) ruff format .
	$(UV_CMD) ruff check --fix .

lint:
	$(UV_CMD) ruff check .
	$(UV_CMD) bandit -r . -c "pyproject.toml" 2>/dev/null || $(UV_CMD) bandit -r main.py

test:
	$(UV_CMD) pytest -v tests/

run:
	$(UV_CMD) python src/main.py

docker-build:
	docker build -t $(PROJECT_NAME):$(TAG) .

docker-scan:
	grype $(PROJECT_NAME):$(TAG)

docker-run:
	docker run -it --rm --name $(PROJECT_NAME) --env-file .env $(PROJECT_NAME):$(TAG)
