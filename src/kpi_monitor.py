from __future__ import annotations

import pandas as pd

SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]


def _build_kpi_row(
    snapshot_date: pd.Timestamp,
    kpi_name: str,
    kpi_value: float,
    unit: str,
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "snapshot_date": snapshot_date.date().isoformat(),
        "kpi_name": kpi_name,
        "kpi_value": round(float(kpi_value), 2),
        "unit": unit,
        "status": status,
        "notes": notes,
    }


def calculate_kpi_snapshot(dataframe: pd.DataFrame) -> pd.DataFrame:
    snapshot_date = pd.to_datetime(dataframe["snapshot_date"].max())

    total_revenue = dataframe["purchase_amount"].sum()
    average_order_value = dataframe["purchase_amount"].mean()
    high_value_customers = dataframe.loc[dataframe["high_value_customer_flag"] == 1, "customer_id"].nunique()
    churn_risk_customers = dataframe.loc[dataframe["churn_risk_flag"] == 1, "customer_id"].nunique()
    inactive_customer_rate = dataframe["inactive_customer_flag"].mean() * 100

    season_revenue = (
        dataframe.groupby("season", as_index=False)["purchase_amount"]
        .sum()
        .set_index("season")
        .reindex(SEASON_ORDER)
        .dropna()
    )

    season_revenue_change_pct = 0.0
    season_note = "Not enough seasonal categories to compare revenue."
    if len(season_revenue) >= 2:
        previous_value = season_revenue["purchase_amount"].iloc[-2]
        current_value = season_revenue["purchase_amount"].iloc[-1]
        if previous_value != 0:
            season_revenue_change_pct = ((current_value - previous_value) / previous_value) * 100
        current_season = season_revenue.index[-1]
        previous_season = season_revenue.index[-2]
        season_note = f"Revenue change from {previous_season} to {current_season}."

    kpis = [
        _build_kpi_row(snapshot_date, "total_revenue", total_revenue, "USD", "ok", "Overall revenue in the dataset."),
        _build_kpi_row(
            snapshot_date,
            "average_order_value",
            average_order_value,
            "USD",
            "ok",
            "Average spend per purchase.",
        ),
        _build_kpi_row(
            snapshot_date,
            "high_value_customers",
            high_value_customers,
            "customers",
            "ok" if high_value_customers >= 500 else "watch",
            "Customers at or above the 75th percentile of purchase amount.",
        ),
        _build_kpi_row(
            snapshot_date,
            "churn_risk_customers",
            churn_risk_customers,
            "customers",
            "watch" if churn_risk_customers > 250 else "ok",
            "Customers with low loyalty, no subscription, and infrequent purchases.",
        ),
        _build_kpi_row(
            snapshot_date,
            "inactive_customer_rate",
            inactive_customer_rate,
            "percent",
            "watch" if inactive_customer_rate > 30 else "ok",
            "Share of customers buying every 90 days or less frequently.",
        ),
        _build_kpi_row(
            snapshot_date,
            "season_revenue_change_pct",
            season_revenue_change_pct,
            "percent",
            "watch" if season_revenue_change_pct < 0 else "ok",
            season_note,
        ),
    ]

    return pd.DataFrame(kpis)


def build_customer_watchlist(dataframe: pd.DataFrame) -> pd.DataFrame:
    watchlist = dataframe.loc[
        (dataframe["high_value_customer_flag"] == 1) | (dataframe["churn_risk_flag"] == 1),
        [
            "customer_id",
            "gender",
            "category",
            "purchase_amount",
            "subscription_status",
            "frequency_of_purchases",
            "customer_segment",
            "high_value_customer_flag",
            "churn_risk_flag",
            "inactive_customer_flag",
            "snapshot_date",
        ],
    ].copy()

    watchlist["priority_label"] = "Monitor"
    watchlist.loc[watchlist["high_value_customer_flag"] == 1, "priority_label"] = "Retain"
    watchlist.loc[watchlist["churn_risk_flag"] == 1, "priority_label"] = "Re-engage"

    return watchlist.sort_values(
        by=["churn_risk_flag", "high_value_customer_flag", "purchase_amount"],
        ascending=[False, False, False],
    )
