from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import ConfigTemplate


class SqlaEngine:
    def __init__(self, config: ConfigTemplate):
        self._engine = create_async_engine(
            config.db_uri,
            echo=True,
        )

    @property
    def engine(self):
        return self._engine

    @property
    def session(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            bind=self._engine,
        )


Base = declarative_base()
