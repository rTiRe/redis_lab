import asyncio
import logging

import aio_pika

from config import settings


logging.basicConfig(level=logging.INFO)


async def main():
    connection = await aio_pika.connect_robust(settings.RABBIT_URL)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        name='logs',
        type=aio_pika.ExchangeType.FANOUT,
        durable=True,
    )
    queue = await channel.declare_queue('logs', durable=True)
    await queue.bind(exchange, 'logs')
    with open('input.txt', 'r') as file:
        for line in file.readlines():
            message = line.strip()
            if not message:
                continue
            await exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key='logs'
            )
            logging.info(f' [x] Sent {message}')
            await asyncio.sleep(1)
    await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
