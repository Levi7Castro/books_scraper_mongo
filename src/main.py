import argparse
import json
import os
from pathlib import Path

from extract_scraper import scrape_all
from load_scraper_mongo import MONGO_URI, get_collection, upsert_books

p = argparse.ArgumentParser()
p.add_argument("--pages", type=int, default=None, help="limite de páginas (padrão: todas)")
p.add_argument("--uri", default=MONGO_URI)
a = p.parse_args()

books = scrape_all(max_pages=a.pages)
out = Path(os.getenv("DATA_DIR", "data")) / "books_raw.json"
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(books, f, default=str, ensure_ascii=False, indent=1)  # camada raw
n = upsert_books(get_collection(a.uri), books)
print(f"{len(books)} livros raspados, {n} gravados/atualizados no MongoDB")