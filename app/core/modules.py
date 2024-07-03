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


def init_routers(app_: FastAPI, config: ConfigTemplate) -> None:
    app_.include_router(router)
    # admin dashboard
    admin = Admin(app_, SqlaEngine(config).engine)
    admin.add_view(UserAdmin)


origins = [
    "*",
    # "http://localhost:8080",
]


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware
