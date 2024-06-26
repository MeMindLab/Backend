import os
from dotenv import load_dotenv

# fastapi
from fastapi import FastAPI
from app.core.modules import init_routers, make_middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="MIMIND backend",
        description="FastAPI",
        version="1.0.0",
        # dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    return app_


# .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")

# .env 파일 로드
load_dotenv(dotenv_path)


app = create_app()
