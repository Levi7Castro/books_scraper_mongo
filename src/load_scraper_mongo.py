"""Carga idempotente no MongoDB (upsert por URL)."""
import os
from datetime import datetime, timezone

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")


def get_collection(uri: str | None = None, db="scraping", coll="books"):
    c = MongoClient(uri or MONGO_URI, serverSelectionTimeoutMS=10_000)[db][coll]
    c.create_index("url", unique=True)
    return c


def upsert_books(collection, books) -> int:
    """Faz upsert por URL e retorna quantos livros são novos ou tiveram dados alterados.

    `scraped_at` (última vez visto) é atualizado em todos, mas fica fora da comparação,
    para que reexecutar sem mudanças no site retorne 0.
    """
    if not books:
        return 0
    changed = 0
    for b in books:
        data = {k: v for k, v in b.items() if k != "scraped_at"}
        first = b.get("scraped_at") or datetime.now(timezone.utc)
        r = collection.update_one(
            {"url": b["url"]},
            {"$set": data, "$setOnInsert": {"first_scraped_at": first}},
            upsert=True,
        )
        changed += int(r.upserted_id is not None or r.modified_count > 0)

    last = max((b.get("scraped_at") for b in books if b.get("scraped_at")),
               default=datetime.now(timezone.utc))
    collection.update_many({"url": {"$in": [b["url"] for b in books]}},
                           {"$set": {"scraped_at": last}})
    return changed
