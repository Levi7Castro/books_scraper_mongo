"""Funções do pipeline, independentes do Airflow (testáveis e reutilizáveis)."""
import json
import os
from datetime import datetime
from pathlib import Path

from extract_scraper import scrape_all
from load_scraper_mongo import MONGO_URI, get_collection, upsert_books

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))


def extract(ds: str, max_pages: int | None = None) -> str:
    """Raspa o site e salva a camada raw em data/raw/books_<ds>.json. Retorna o caminho."""
    books = scrape_all(max_pages=max_pages)
    path = DATA_DIR / "raw" / f"books_{ds}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(books, default=str, ensure_ascii=False, indent=1), encoding="utf-8")
    return str(path)


def load(path: str, uri: str = MONGO_URI) -> int:
    """Lê o JSON raw e faz upsert no MongoDB."""
    books = json.loads(Path(path).read_text(encoding="utf-8"))
    for b in books:
        b["scraped_at"] = datetime.fromisoformat(b["scraped_at"])
    return upsert_books(get_collection(uri), books)