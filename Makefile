.PHONY: all
all:


.PHONY: format
format:
	poetry run isort ./src ./tests
	poetry run black ./src ./tests --experimental-string-processing
	poetry run ruff check ./src ./tests --fix
	poetry run mypy ./src ./tests


.PHONY: migration_init
migration_init:
	docker-compose exec fastapi /bin/bash -c "poetry run alembic upgrade head"


.PHONY: server
server:
	python -m server
