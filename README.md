# Books Scraper → MongoDB

Projeto de dados: coleta (web scraping) → camada raw (JSON) → carga em banco NoSQL (MongoDB) → consultas com aggregation pipeline.

**Fonte:** https://books.toscrape.com (site feito para praticar scraping). Stack: Python, requests, BeautifulSoup, MongoDB (Docker), pytest.

## Como rodar

### 1. Credenciais
```bash
cp .env.example .env   # preencha AIRFLOW_PASSWORD, MONGO_PASSWORD, POSTGRES_PASSWORD e AIRFLOW_FERNET_KEY; AIRFLOW_UID = saída de `id -u`
```
> Evite `@ : / %` na senha do Mongo (ela entra na URI de conexão). O usuário do Mongo (e a senha do Postgres) só são aplicados quando os volumes `mongo_data` / `pg_data` estão vazios. As portas 8080 e 27017 ficam acessíveis só em `localhost`.

### 2. Airflow + MongoDB (Docker)
```bash
docker compose up -d --build
```
- UI do Airflow: http://localhost:8080 (login com `AIRFLOW_USER` / `AIRFLOW_PASSWORD`)
- DAG `books_scraper_mongo`: roda todo dia às 06:00. Para teste rápido, use *Trigger DAG w/ config* com `{"max_pages": 2}`.

### 3. Local (fora do Docker)
```bash
uv sync
export MONGO_URI="mongodb://<usuario>:<senha>@localhost:27017/?authSource=admin"
cd src && uv run python main.py --pages 3   # sem --pages raspa as 50 páginas
uv run python queries.py                    # consultas analíticas
cd .. && uv run pytest -q                   # testes (parser, idempotência, pipeline)
```

## Decisões
- **requests + BS4** em vez de Selenium: o site é HTML estático; Selenium só se justifica com conteúdo renderizado por JS.
- **Upsert por `url`** (índice único): rodar de novo não duplica, só atualiza. A carga retorna quantos livros são novos ou mudaram; `scraped_at` guarda a última vez em que o livro foi visto e `first_scraped_at` a primeira.
- **Raw em JSON** antes da carga, para reprocessar sem raspar de novo.
- `time.sleep` entre requisições para não sobrecarregar o servidor.

## Próximos passos
Guardar histórico de preço (SCD), dashboard no Power BI via conector MongoDB/Python.
