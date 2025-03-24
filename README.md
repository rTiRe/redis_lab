# Практическая работа №2 - Тюрин Артём К0709-22

Docker Compose присутствует, **но** для запуска лучше воспользоваться тем, что лежит в папке scripts, потому что `.env` файлы лежат не в той же директории, что и `docker-compose.yml`, а он из-за этого будет выделываться. Запускать скрипты из основной папки, не из `scripts/`!

#### Запустить в detached режиме
```
scripts/remote.sh start
```

#### Посмотреть логи
```
scripts/remote.sh logs
```

#### Перезапустить
```
scripts/remote.sh restart
```

#### Остановить
```
scripts/remote.sh stop
```

#### Запустить в attchaed режиме
```
scripts/remote.sh start_attached
```

#### Собрать/пересобрать
```
scripts/remote.sh rebuild
```

После каждой из команд можно указывать название контейнера, к котрому ее применить, из доступных: `consumer` и `publisher`.

Перед запуском настроить `.env` внутри `consumer/config` и `publisher/config`. Будет достаточно просто переименовать `.env.example` в `.env`.

## Доп требования
- **Exchange**: Fanout 📢
- **Cassandra**: поднята 🆙
- Сон: отсутствует
- Артём: Тюрин