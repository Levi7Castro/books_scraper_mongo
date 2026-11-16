from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.models.param import Param


@dag(
    dag_id="books_scraper_mongo",
    schedule="0 6 * * *",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
    params={
        "max_pages": Param(
            None,
            type=["null", "integer"],
            minimum=1,
            title="Máximo de páginas",
            description="Deixe vazio para raspar todas as 50 páginas. Use 2 ou 3 para um teste rápido.",
        ),
    },
    tags=["scraping", "mongodb"],
)
def books_scraper_mongo():
    @task
    def extract(ds=None, params=None):
        from pipeline import extract as _extract
        max_pages = params.get("max_pages")
        return _extract(ds, int(max_pages) if max_pages not in (None, "") else None)

    @task
    def load(path: str):
        from pipeline import load as _load
        n = _load(path)
        print(f"{n} documentos gravados/atualizados")
        return n

    load(extract())



books_scraper_mongo()
