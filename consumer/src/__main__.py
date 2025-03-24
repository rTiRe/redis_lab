import asyncio

import aio_pika
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

from src.storage import cassandra
from config import settings


async def callback(message: aio_pika.IncomingMessage) -> str:
    async with message.process():
        body = message.body.decode()
        print(f' [x] Consumer {settings.NAME} received {body}')
        query = SimpleStatement("""
            INSERT INTO messages_consumer1 (id, message)
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
    await queue.bind(exchange, routing_key='')
    cassandra.session.execute("""
        CREATE TABLE IF NOT EXISTS messages_consumer1 (
            id UUID PRIMARY KEY,
            message TEXT
        )
    """)
    await queue.consume(callback)
    print(f' [*] Consumer {settings.NAME} waiting for messages')
    await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
