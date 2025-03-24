import asyncio

import aio_pika

from config import settings


async def main():
    connection = await aio_pika.connect_robust(settings.RABBIT_URL)
    channel = await connection.channel()
    await channel.declare_exchange(
        name='logs',
        type=aio_pika.ExchangeType.FANOUT,
        durable=True,
    )
    with open('input.txt', 'r') as file:
        for line in file.readlines():
            message = line.strip()
            if not message:
                continue
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key='logs'
            )
            print(f' [x] Sent {message}')
            await asyncio.sleep(1)
    await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
