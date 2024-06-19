#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# You can put other setup logic here

# 데이터베이스 마이그레이션 실행
alembic upgrade head

# Evaluating passed command:
exec "$@"