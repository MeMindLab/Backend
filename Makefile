.PHONY: all
all:

.PHONY: migration_init
migration_init:
	docker-compose exec fastapi /bin/bash -c "poetry run alembic upgrade head"

.PHONY: server
server:
	python -m server
