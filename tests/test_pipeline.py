import mongomock
from extract_scraper import parse_page
from load_scraper_mongo import upsert_books

HTML = """<html><body><ol>
<li><article class="product_pod"><p class="star-rating Three"></p>
<h3><a href="a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light...</a></h3>
<div class="product_price"><p class="price_color">£51.77</p>
<p class="instock availability"> In stock </p></div></article></li>
<li><article class="product_pod"><p class="star-rating Five"></p>
<h3><a href="tipping-the-velvet_999/index.html" title="Tipping the Velvet">Tipping...</a></h3>
<div class="product_price"><p class="price_color">£53.74</p>
<p class="instock availability"> In stock </p></div></article></li>
</ol><ul class="pager"><li class="next"><a href="page-2.html">next</a></li></ul></body></html>"""

def test_parse():
    books, nxt = parse_page(HTML, "https://books.toscrape.com/catalogue/page-1.html")
    assert len(books) == 2 and books[0]["price_gbp"] == 51.77 and books[1]["rating"] == 5
    assert nxt.endswith("catalogue/page-2.html")

def test_upsert_idempotente():
    c = mongomock.MongoClient().db.books
    books, _ = parse_page(HTML, "https://books.toscrape.com/catalogue/page-1.html")
    assert upsert_books(c, books) == 2   # inseridos
    assert upsert_books(c, books) == 0   # nada mudou
    assert c.count_documents({}) == 2
    books[0]["price_gbp"] = 10.0
    assert upsert_books(c, books) == 1   # só o alterado
    doc = c.find_one({"url": books[0]["url"]})
    assert doc["price_gbp"] == 10.0 and "first_scraped_at" in doc and "scraped_at" in doc

def test_extract_load(tmp_path, monkeypatch):
    import pipeline
    monkeypatch.setattr(pipeline, "DATA_DIR", tmp_path)
    books, _ = parse_page(HTML, "https://books.toscrape.com/catalogue/page-1.html")
    monkeypatch.setattr(pipeline, "scrape_all", lambda max_pages=None: books)
    mock = mongomock.MongoClient().db.books
    monkeypatch.setattr(pipeline, "get_collection", lambda uri: mock)
    path = pipeline.extract("2026-11-15")
    assert pipeline.load(path) == 2
    assert mock.count_documents({}) == 2