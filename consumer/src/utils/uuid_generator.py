import uuid


async def uuid_generator(message: str | bytes) -> uuid.UUID:
    return uuid.uuid5(uuid.NAMESPACE_X500, message)
