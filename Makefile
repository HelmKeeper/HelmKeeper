.PHONY: install test lint format clean build build-docker run-docker

install:
	poetry install

test:
	poetry run pytest --cov=main --cov-report=term-missing test/

lint:
	poetry run ruff check .
	poetry run black --check .

format:
	poetry run black .
	poetry run ruff check --fix .

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf *.egg-info

build-docker:
	docker build -t helmkeeper:latest .

run-docker:
	docker run --rm -v $(PWD):/app helmkeeper:latest ./test/resources/gitlab --check
