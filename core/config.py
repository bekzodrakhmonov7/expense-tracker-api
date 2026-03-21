from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str

    jwt_token: SecretStr
    jwt_algo: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

