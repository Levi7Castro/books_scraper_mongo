"""Exemplos de consultas analíticas (aggregation pipeline)."""
from load_scraper_mongo import get_collection

c = get_collection()
print("Preço médio por nota:")
for r in c.aggregate([
    {"$group": {"_id": "$rating", "preco_medio": {"$avg": "$price_gbp"}, "qtd": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
]):
    print(r)
print("Top 5 mais caros:")
for r in c.find({}, {"_id": 0, "title": 1, "price_gbp": 1}).sort("price_gbp", -1).limit(5):
    print(r)