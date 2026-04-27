from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "customer_shopping_behavior.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "customer_behavior_enriched.csv"
WATCHLIST_PATH = PROJECT_ROOT / "outputs" / "customer_watchlist.csv"
KPI_SNAPSHOT_PATH = PROJECT_ROOT / "outputs" / "kpi_snapshot_latest.csv"
ALERTS_PATH = PROJECT_ROOT / "outputs" / "alerts_latest.csv"

FREQUENCY_TO_DAYS = {
    "Weekly": 7,
    "Bi-Weekly": 14,
    "Fortnightly": 14,
    "Monthly": 30,
    "Quarterly": 90,
    "Every 3 Months": 90,
    "Annually": 365,
}


def _normalize_column_name(column_name: str) -> str:
    clean_name = column_name.replace("\ufeff", "").strip().lower()
    clean_name = clean_name.replace("(", "").replace(")", "")
    clean_name = clean_name.replace("/", " ")
    clean_name = "_".join(clean_name.split())
    return clean_name


def load_raw_data(file_path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    dataframe = pd.read_csv(file_path)
    dataframe.columns = [_normalize_column_name(col) for col in dataframe.columns]
    return dataframe


def transform_customer_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()

    numeric_columns = ["customer_id", "age", "purchase_amount_usd", "review_rating", "previous_purchases"]
    for column_name in numeric_columns:
        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")

    df = df.rename(columns={"purchase_amount_usd": "purchase_amount"})
    df["purchase_frequency_days"] = df["frequency_of_purchases"].map(FREQUENCY_TO_DAYS).fillna(30)

    age_bins = [0, 25, 35, 50, 100]
    age_labels = ["18-25", "26-35", "36-50", "51+"]
    df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, include_lowest=True)

    df["customer_segment"] = pd.cut(
        df["previous_purchases"],
        bins=[-1, 2, 10, float("inf")],
        labels=["New", "Returning", "Loyal"],
    )

    high_value_threshold = df["purchase_amount"].quantile(0.75)
    df["high_value_customer_flag"] = (df["purchase_amount"] >= high_value_threshold).astype(int)

    df["inactive_customer_flag"] = (df["purchase_frequency_days"] >= 90).astype(int)
    df["churn_risk_flag"] = (
        (df["subscription_status"].eq("No"))
        & (df["purchase_frequency_days"] >= 90)
        & (df["previous_purchases"] <= 5)
    ).astype(int)

    df["snapshot_date"] = pd.Timestamp.today().normalize()

    return df


def save_outputs(
    enriched_df: pd.DataFrame,
    kpi_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
) -> None:
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    enriched_df.to_csv(PROCESSED_DATA_PATH, index=False)
    kpi_df.to_csv(KPI_SNAPSHOT_PATH, index=False)
    watchlist_df.to_csv(WATCHLIST_PATH, index=False)
    alerts_df.to_csv(ALERTS_PATH, index=False)


def build_sql_server_engine():
    server = os.getenv("SQL_SERVER_HOST")
    database = os.getenv("SQL_SERVER_DATABASE")
    username = os.getenv("SQL_SERVER_USER")
    password = os.getenv("SQL_SERVER_PASSWORD")
    port = os.getenv("SQL_SERVER_PORT", "1433")
    driver = quote_plus(os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server"))

    if not all([server, database, username, password]):
        raise ValueError(
            "Missing SQL Server connection settings. "
            "Set SQL_SERVER_HOST, SQL_SERVER_DATABASE, SQL_SERVER_USER and SQL_SERVER_PASSWORD."
        )

    connection_url = (
        f"mssql+pyodbc://{username}:{password}@{server},{port}/{database}?driver={driver}"
    )
    return create_engine(connection_url)


def export_to_sql_server(
    enriched_df: pd.DataFrame,
    kpi_df: pd.DataFrame,
    watchlist_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
) -> None:
    engine = build_sql_server_engine()

    enriched_df.to_sql("customer_behavior_enriched", engine, schema="dbo", if_exists="replace", index=False)
    kpi_df.to_sql("kpi_snapshot", engine, schema="dbo", if_exists="replace", index=False)
    watchlist_df.to_sql("customer_watchlist", engine, schema="dbo", if_exists="replace", index=False)
    alerts_df.to_sql("automation_alerts", engine, schema="dbo", if_exists="replace", index=False)
