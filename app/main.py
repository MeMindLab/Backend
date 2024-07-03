# fastapi
from fastapi import FastAPI
from app.core.modules import init_routers, make_middleware
from app.core.config import get_config


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="MIMIND backend",
        description="FastAPI",
        version="1.0.0",
        # dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_, config=get_config())
    return app_


app = create_app()
