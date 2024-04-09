PROJECT_NAME = .hack_template
TEST_PATH = ./tests/

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

lint-ci: flake ruff bandit mypy  ##@Linting Run all linters in CI

flake: ##@Linting Run flake8
	.venv/bin/flake8 --max-line-length 88 --format=default ./$(PROJECT_NAME) 2>&1 | tee flake8.txt

ruff: ##@Linting Run ruff
	.venv/bin/ruff check ./$(PROJECT_NAME)

mypy: ##@Linting Run mypy
	.venv/bin/mypy --config-file ./pyproject.toml ./$(PROJECT_NAME)

test: ##@Test Run tests with pytest
	pytest -vvx $(TEST_PATH)

test-ci: ##@Test Run tests with pytest and coverage in CI
	.venv/bin/pytest $(TEST_PATH) --junitxml=./junit.xml --cov=./$(PROJECT_NAME) --cov-report=xml

develop: #
	python -m venv .venv
	.venv/bin/pip install -U pip poetry
	.venv/bin/poetry config virtualenvs.create false
	.venv/bin/poetry install

local: ##@Develop Run dev containers for test
	docker compose -f docker-compose.dev.yaml up --force-recreate --renew-anon-volumes --build

local_down: ##@Develop Stop dev containers with delete volumes
	docker compose -f docker-compose.dev.yaml down -v

alembic-upgrade-head:
	.venv/bin/python -m hack_template.db --pg-dsn=$(APP_PG_DSN) upgrade head

alembic-downgrade:
	.venv/bin/python -m hack_template.db --pg-dsn=$(APP_PG_DSN) downgrade -1