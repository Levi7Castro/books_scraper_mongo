"""Scraper de books.toscrape.com (site de prática) usando requests + BeautifulSoup."""
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/"
START = BASE + "page-1.html"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HEADERS = {"User-Agent": "Mozilla/5.0 (projeto-estudo-dados)"}


def parse_page(html: str, page_url: str):
    """Retorna (lista de livros, url da próxima página ou None)."""
    soup = BeautifulSoup(html, "lxml")
    books = []
    for art in soup.select("article.product_pod"):
        a = art.h3.a
        price = float(re.sub(r"[^\d.]", "", art.select_one(".price_color").text))
        rating_cls = [c for c in art.select_one("p.star-rating")["class"] if c != "star-rating"][0]
        books.append({
            "title": a["title"],
            "url": urljoin(page_url, a["href"]),
            "price_gbp": price,
            "rating": RATING.get(rating_cls),
            "in_stock": "in stock" in art.select_one(".availability").text.lower(),
            "scraped_at": datetime.now(timezone.utc),
        })
    nxt = soup.select_one("li.next a")
    return books, (urljoin(page_url, nxt["href"]) if nxt else None)


def scrape_all(max_pages: int | None = None, delay: float = 0.5):
    url, n, out = START, 0, []
    session = requests.Session()
    session.headers.update(HEADERS)
    while url and (max_pages is None or n < max_pages):
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        books, url = parse_page(resp.text, resp.url)
        out.extend(books)
        n += 1
        time.sleep(delay)  # educado com o servidor
    return out