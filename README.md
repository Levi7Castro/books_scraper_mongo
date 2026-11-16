# Books Scraper → MongoDB

Projeto de dados: coleta (web scraping) → camada raw (JSON) → carga em banco NoSQL (MongoDB) → consultas com aggregation pipeline.

**Fonte:** https://books.toscrape.com (site feito para praticar scraping). Stack: Python, requests, BeautifulSoup, MongoDB (Docker), pytest.

## Como rodar
```bash
docker compose up -d          # sobe o MongoDB
pip install -r requirements.txt
cd src && python main.py --pages 3   # teste rápido; sem --pages raspa as 50 páginas
python queries.py             # consultas analíticas
pytest -q tests               # testes (parser + idempotência da carga)
```

## Decisões
- **requests + BS4** em vez de Selenium: o site é HTML estático; Selenium só se justifica com conteúdo renderizado por JS.
- **Upsert por `url`** (índice único): rodar de novo não duplica, só atualiza.
- **Raw em JSON** antes da carga, para reprocessar sem raspar de novo.
- `time.sleep` entre requisições para não sobrecarregar o servidor.

## Próximos passos
Orquestrar com Airflow (DAG diária), guardar histórico de preço (SCD), dashboard no Power BI via conector MongoDB/Python.
