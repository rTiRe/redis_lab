import asyncio
import logging
from uuid import UUID
import json

import aio_pika
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

from src.storage import cassandra, redis
from config import settings
from src.utils import uuid_generator


logging.basicConfig(level=logging.INFO)


async def save_to_cassandra(
    id: str | UUID,
    message: str | None = None,
    select_from_database_id: str | None = None,
) -> None:
    if not message:
        if not select_from_database_id:
            logging.exception(f' [x] select_from_database_id needed')
            raise ValueError('select_from_database_id needed')
        get_message_query = SimpleStatement(
            f'SELECT message FROM messages_{select_from_database_id} WHERE hash_id = %s',
            consistency_level=ConsistencyLevel.ONE
        )
        result = cassandra.session.execute(get_message_query, (id,))
        if result:
            message = result.one().message
            logging.info(f' [x] Retrieved existing message from Cassandra: {message}')
        else:
            logging.exception(f' [x] No message found in Cassandra for hash id {id}')
            raise ValueError(f'No message found in Cassandra for hash id {id}')
    save_message_query = SimpleStatement(f"""
        INSERT INTO messages_{settings.NAME} (id, message, hash_id)
        VALUES (uuid(), %s, %s)
    """, consistency_level=ConsistencyLevel.ONE)
    cassandra.session.execute(save_message_query, (message, id))


async def process_message(message_id: str | UUID, message: str) -> str:
    # Very resource intensive processing
    logging.info(f' [x] Processing message: {message_id}')
    await asyncio.sleep(2)
    return message


async def wait_for_redis_lock_release(message_id: str | UUID, timeout: int = 30) -> bool:
    lock_key = f'{redis.LOCK_PREFIX}{message_id}'
    check_interval = 0.5
    for _ in range(int(timeout / check_interval)):
        if not await redis.redis.exists(lock_key):
            return True
        await asyncio.sleep(check_interval)
    return False


async def check_redis(message_id: str | UUID) -> tuple[bool, str | None]:
    lock_key = f'{redis.LOCK_PREFIX}{message_id}'
    processed_key = f'{redis.PROCESSED_PREFIX}{message_id}'
    if await redis.redis.exists(processed_key):
        logging.info(f' [x] Message {message_id} already processed')
        database_id: str = (await redis.redis.get(processed_key)).decode()
        return False, database_id
    acquired = await redis.redis.set(lock_key, '1', nx=True, ex=30)
    if acquired:
        return True, None
    logging.info(f' [x] Message {message_id} is being processed by another consumer, waiting...')
    if await wait_for_redis_lock_release(message_id):
        if await redis.redis.exists(processed_key):
            logging.info(f' [x] Message {message_id} was processed while waiting')
            database_id: str = (await redis.redis.get(processed_key)).decode()
            return False, database_id
        return await check_redis(message_id)
    logging.warning(f' [x] Timeout waiting for message {message_id} lock release')
    return False, None


async def callback(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        uuid = await uuid_generator(message.body)
        body = message.body.decode()
        logging.info(f' [x] Consumer {settings.NAME} received {body} (id {uuid})')
        checked_redis, database_id = await check_redis(uuid)
        processed_message = None
        if checked_redis:
            processed_key = f'{redis.PROCESSED_PREFIX}{uuid}'
            lock_key = f'{redis.LOCK_PREFIX}{uuid}'
            try:
                processed_message = await process_message(uuid, body)
                await redis.redis.setex(processed_key, 86400, settings.NAME)
                await save_to_cassandra(uuid, processed_message)
            except Exception as exception:
                logging.exception(exception)
                return
            finally:
                await redis.redis.delete(lock_key)
            return
        if database_id:
            try:
                await save_to_cassandra(uuid, select_from_database_id=database_id)
            except Exception as exception:
                logging.exception(exception)
                return


async def main():
    connection = await aio_pika.connect_robust(settings.RABBIT_URL)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        name='logs',
        type=aio_pika.ExchangeType.FANOUT,
        durable=True,
    )
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange, 'logs')
    await queue.consume(callback)
    logging.info(f' [*] Consumer {settings.NAME} waiting for messages')
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
