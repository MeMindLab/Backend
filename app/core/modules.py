import sentry_sdk

# fastapi
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# sqlalchemy
from sqladmin import Admin

# import
from app.core.database import SqlaEngine
from app.models.admin import UserAdmin
from app.api.routers.api import router
from app.core.config import ConfigTemplate
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration


def init_routers(app_: FastAPI, config: ConfigTemplate) -> None:
    app_.include_router(router)
    # admin dashboard
    admin = Admin(app_, SqlaEngine(config).engine)
    admin.add_view(UserAdmin)


origins = [
    "*",
]


def make_middleware(config) -> List[Middleware]:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        enable_tracing=True,
        traces_sample_rate=0.6,
        integrations=[
            LoggingIntegration(),
        ],
    )

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SentryAsgiMiddleware),
    ]
    return middleware
