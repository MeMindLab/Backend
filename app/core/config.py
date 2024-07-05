import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigTemplate(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.expandvars(".env"),
        env_file_encoding="utf-8",
    )

    DATABASE_USER: str = "dev"
    DATABASE_PASSWORD: str = "dev1234"
    # DATABASE_HOST: str = "localhost"
    DATABASE_HOST: str = "memind-postgres"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "dev"

    SECRET_KEY: str = "09027e5d4c40783326cef1ee95c179c7dcaa4c92e90844c1c1958b027546d240"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5  # 5분
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    TWILIO_VERIFY_SERVICE_SID: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    OPENAI_API_KEY: str

    SERVER_HOST: str = "http://localhost:8000"

    MAX_UPLOAD_IMAGE_SIZE: int = 1024 * 1024 * 10  # 10MB

    @property
    def db_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


config = ConfigTemplate()


def get_config() -> ConfigTemplate:
    return config
