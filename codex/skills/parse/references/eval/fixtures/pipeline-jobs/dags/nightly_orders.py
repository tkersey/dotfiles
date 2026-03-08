"""Airflow DAG for the nightly orders pipeline."""

from jobs.extract_orders import extract


def build_dag() -> None:
    extract()
