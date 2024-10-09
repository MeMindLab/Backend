# fastapi
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.modules import init_routers, make_middleware
from app.core.config import get_config

# import
from sentry_sdk import capture_exception

from app.exceptions.exception import ServiceException


def create_app() -> FastAPI:
    config = get_config()
    app_ = FastAPI(
        title="MEMIND backend",
        description="FastAPI",
        version="1.0.0",
        middleware=make_middleware(config),
    )
    init_routers(app_=app_, config=config)
    return app_


app = create_app()


@app.exception_handler(ServiceException)
async def global_exception_handler(request: Request, exc: ServiceException):
    if exc.status_code == 500:
        capture_exception(exc)

    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )
