from __future__ import annotations

import os

from src.automation_runner import evaluate_alerts, load_previous_kpis
from src.data_loader import export_to_sql_server, load_raw_data, save_outputs, transform_customer_data
from src.kpi_monitor import build_customer_watchlist, calculate_kpi_snapshot


def main() -> None:
    raw_df = load_raw_data()
    enriched_df = transform_customer_data(raw_df)

    previous_kpi_df = load_previous_kpis()
    kpi_df = calculate_kpi_snapshot(enriched_df)
    watchlist_df = build_customer_watchlist(enriched_df)
    alerts_df = evaluate_alerts(kpi_df, previous_kpi_df)

    save_outputs(enriched_df, kpi_df, watchlist_df, alerts_df)

    if os.getenv("LOAD_TO_SQL_SERVER", "false").lower() == "true":
        export_to_sql_server(enriched_df, kpi_df, watchlist_df, alerts_df)
        print("Pipeline completed. Files were saved locally and loaded into SQL Server.")
    else:
        print("Pipeline completed. Files were saved locally.")
        print("Set LOAD_TO_SQL_SERVER=true to push the outputs to SQL Server.")


if __name__ == "__main__":
    main()
