from pymongo import MongoClient

from acta_mcp.core.config import Settings


def create_mongo_client(settings: Settings) -> MongoClient:
    return MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=settings.acta_mongo_timeout_ms,
        connect=False,
    )

