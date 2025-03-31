from redis.asyncio import Redis

from config import settings


class Database():
    LOCK_PREFIX = 'lock:'
    PROCESSED_PREFIX = 'processed:'

    def __init__(self) -> None:
        self.__redis = Redis.from_url(settings.REDIS_URL)

    @property
    def redis(self) -> Redis:
        return self.__redis


redis = Database()
