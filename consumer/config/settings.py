from os import getenv

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RABBIT_URL: str
    DB_CLUSTER: str
    DB_KEYSPACE: str
    REDIS_URL: str
    NAME: str = getenv('HOSTNAME')

    class Config:
        env_file = 'config/.env'


settings = Settings()
