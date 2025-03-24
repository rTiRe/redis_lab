from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBIT_URL: str

    class Config:
        env_file = 'config/.env'


settings = Settings()
