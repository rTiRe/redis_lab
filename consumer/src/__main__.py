import asyncio
import logging

import aio_pika
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

from src.storage import cassandra
from config import settings


logging.basicConfig(level=logging.INFO)


async def callback(message: aio_pika.IncomingMessage) -> str:
    async with message.process():
        body = message.body.decode()
        logging.info(f' [x] Consumer {settings.NAME} received {body}')
        query = SimpleStatement(f"""
            INSERT INTO messages_{settings.NAME} (id, message)
            VALUES (uuid(), %s)
        """, consistency_level=ConsistencyLevel.ONE)
        cassandra.session.execute(query, (body,))


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
