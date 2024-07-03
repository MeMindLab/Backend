from fastapi import Depends

from app.core.database import SqlaEngine
from app.core.config import ConfigTemplate, get_config


async def get_db(
    config: ConfigTemplate = Depends(get_config),
):
    session = SqlaEngine(config).session()

    if session is None:
        raise Exception("session is not connected")
    try:
        yield session
    finally:
        await session.close()
