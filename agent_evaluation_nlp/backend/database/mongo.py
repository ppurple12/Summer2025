from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
import os
import asyncio


MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,  # set True only for debugging
)
db = client[MONGO_DB]

def get_documents_collection() -> AsyncIOMotorCollection:
    return db["documents_doc"]

def get_roles_collection() -> AsyncIOMotorCollection:
    return db["roles_doc"]

