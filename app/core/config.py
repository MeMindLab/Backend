import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigTemplate(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.expandvars(".env"),
        env_file_encoding="utf-8",
    )

    INITIAL_LEMON_COUNT: int = int(os.environ.get("INITIAL_LEMON_COUNT", 1))
    REFERRAL_LEMON_BONUS: int = int(os.environ.get("REFERRAL_LEMON_BONUS", 5))

    LEMON_COUNT_FOR_VERIFIED_USER: int = int(
        os.environ.get("LEMON_COUNT_FOR_VERIFIED_USER", 5)
    )

    DATABASE_USER: str = "dev"
    DATABASE_PASSWORD: str = "dev1234"
    DATABASE_HOST: str = "memind-postgres"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "dev"

    SUPABASE_DATABASE_USER: str = os.environ.get("SUPABASE_DATABASE_USER")
    SUPABASE_DATABASE_PASSWORD: str = os.environ.get("SUPABASE_DATABASE_PASSWORD")
    SUPABASE_DATABASE_HOST: str = os.environ.get("SUPABASE_DATABASE_HOST")
    SUPABASE_DATABASE_PORT: int = int(os.environ.get("SUPABASE_DATABASE_PORT", 5432))
    SUPABASE_DATABASE_NAME: str = os.environ.get("SUPABASE_DATABASE_NAME")

    SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
    SUPABASE_BUCKET: str = os.environ.get("SUPABASE_BUCKET", "memind-image")

    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15분
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    TWILIO_VERIFY_SERVICE_SID: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    OPENAI_API_KEY: str

    SERVER_HOST: str = "http://localhost:8000"

    MAX_UPLOAD_IMAGE_SIZE: int = 1024 * 1024 * 10  # 10MB
    SENTRY_DSN: str = os.environ.get("SENTRY_DSN")

    @property
    def db_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.SUPABASE_DATABASE_USER}:{self.SUPABASE_DATABASE_PASSWORD}@"
            f"{self.SUPABASE_DATABASE_HOST}:{self.SUPABASE_DATABASE_PORT}/{self.SUPABASE_DATABASE_NAME}"
        )


config = ConfigTemplate()


def get_config() -> ConfigTemplate:
    return config
