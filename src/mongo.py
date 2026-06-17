from backend.config.settings import settings

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ModuleNotFoundError:
    AsyncIOMotorClient = None  # type: ignore

if AsyncIOMotorClient is not None:
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]
else:
    client = None
    db = {}


def get_database():
    return db


async def close_database():
    if client is not None:
        client.close()
