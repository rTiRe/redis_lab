from cassandra.cluster import Cluster, Session

from config import settings


class Database():
    def __init__(self) -> None:
        self.__cluster = Cluster([settings.DB_CLUSTER])
        self.__session = self.__cluster.connect()
        self.__session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {settings.DB_KEYSPACE}
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
        """)
        self.__session.set_keyspace(settings.DB_KEYSPACE)
        self.__session.execute(f"""
            CREATE TABLE IF NOT EXISTS messages_{settings.NAME} (
                id UUID PRIMARY KEY,
                message TEXT
            )
        """)

    @property
    def session(self) -> Session:
        return self.__session


cassandra = Database()
