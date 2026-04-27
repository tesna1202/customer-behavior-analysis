from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PREVIOUS_KPI_PATH = PROJECT_ROOT / "outputs" / "kpi_snapshot_latest.csv"


def load_previous_kpis(file_path: Path | str = PREVIOUS_KPI_PATH) -> pd.DataFrame:
    path = Path(file_path)
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=["snapshot_date", "kpi_name", "kpi_value", "unit", "status", "notes"])


def evaluate_alerts(current_kpis: pd.DataFrame, previous_kpis: pd.DataFrame) -> pd.DataFrame:
    current_map = current_kpis.set_index("kpi_name")["kpi_value"].to_dict()
    previous_map = previous_kpis.set_index("kpi_name")["kpi_value"].to_dict() if not previous_kpis.empty else {}
    snapshot_date = current_kpis["snapshot_date"].iloc[0]

    alerts: list[dict[str, object]] = []

    total_revenue = current_map.get("total_revenue", 0)
    previous_revenue = previous_map.get("total_revenue")
    if previous_revenue:
        revenue_change_pct = ((total_revenue - previous_revenue) / previous_revenue) * 100
        if revenue_change_pct <= -10:
            alerts.append(
                {
                    "snapshot_date": snapshot_date,
                    "alert_type": "Revenue drop",
                    "severity": "High",
                    "message": f"Revenue dropped by {revenue_change_pct:.2f}% compared with the previous snapshot.",
                }
            )

    churn_risk_customers = current_map.get("churn_risk_customers", 0)
    if churn_risk_customers > 250:
        alerts.append(
            {
                "snapshot_date": snapshot_date,
                "alert_type": "Churn risk",
                "severity": "Medium",
                "message": "More than 250 customers are currently marked as churn risk.",
            }
        )

    inactive_customer_rate = current_map.get("inactive_customer_rate", 0)
    if inactive_customer_rate > 30:
        alerts.append(
            {
                "snapshot_date": snapshot_date,
                "alert_type": "Inactive customers",
                "severity": "Medium",
                "message": "Inactive customer rate is above 30% and should be reviewed.",
            }
        )

    season_revenue_change_pct = current_map.get("season_revenue_change_pct", 0)
    if season_revenue_change_pct < 0:
        alerts.append(
            {
                "snapshot_date": snapshot_date,
                "alert_type": "Seasonal revenue trend",
                "severity": "Low",
                "message": "Revenue is lower than in the previous season segment.",
            }
        )

    if not alerts:
        alerts.append(
            {
                "snapshot_date": snapshot_date,
                "alert_type": "No alert",
                "severity": "Info",
                "message": "No automation rules were triggered in this run.",
            }
        )

    return pd.DataFrame(alerts)
